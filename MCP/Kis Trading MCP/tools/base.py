from abc import ABC, abstractmethod
from typing import Dict, Any, List
import json
import os
import time
import shutil
import subprocess
import requests
from fastmcp import FastMCP, Context

from module.plugin import MasterFileManager
from module.plugin.database import Database
import module.factory as factory


class ApiExecutor:
    """API 실행 클래스 - GitHub에서 코드를 다운로드하고 실행"""

    def __init__(self, tool_name: str):
        """초기화"""
        self.tool_name = tool_name
        self.temp_base_dir = "./tmp"
        # 절대 경로로 venv python 설정
        self.venv_python = os.path.join(os.getcwd(), ".venv", "bin", "python")

        # temp 디렉토리 생성
        os.makedirs(self.temp_base_dir, exist_ok=True)

    def _create_temp_directory(self, request_id: str) -> str:
        """임시 디렉토리 생성"""
        timestamp = int(time.time() * 1_000_000)  # 나노초 단위
        temp_dir = os.path.join(self.temp_base_dir, f"{timestamp}_{request_id}")
        os.makedirs(temp_dir, exist_ok=True)
        return temp_dir

    @classmethod
    def _download_file(cls, url: str, file_path: str) -> bool:
        """파일 다운로드"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
            return True
        except Exception as e:
            print(f"파일 다운로드 실패: {url}, 오류: {str(e)}")
            return False

    def _download_kis_auth(self, temp_dir: str) -> bool:
        """kis_auth.py 다운로드"""
        kis_auth_url = "https://raw.githubusercontent.com/koreainvestment/open-trading-api/main/examples_llm/kis_auth.py"
        kis_auth_path = os.path.join(temp_dir, "kis_auth.py")
        return self._download_file(kis_auth_url, kis_auth_path)

    def _download_api_code(self, github_url: str, temp_dir: str, api_type: str) -> str:
        """API 코드 다운로드"""
        # GitHub URL을 raw URL로 변환하고 api_type/api_type.py를 붙여서 실제 파일 경로 생성
        raw_url = github_url.replace('/tree/', '/').replace('github.com', 'raw.githubusercontent.com')
        full_url = f"{raw_url}/{api_type}.py"
        api_code_path = os.path.join(temp_dir, "api_code.py")

        if self._download_file(full_url, api_code_path):
            return api_code_path
        else:
            raise Exception(f"API 코드 다운로드 실패: {full_url}")

    @classmethod
    def _extract_trenv_params_from_example(cls, api_code_content: str) -> Dict[str, str]:
        """예제 파일에서 trenv 사용 패턴 완전 추출"""
        import re
        
        # 🎯 완전 자동화: param_name=xxx.my_attr 패턴 찾기 (변수명 무관)
        trenv_mapping_pattern = r'(\w+)=\w*\.(my_\w+)'
        matches = re.findall(trenv_mapping_pattern, api_code_content)
        
        dynamic_mappings = {}
        discovered_mappings = []
        
        for param_name, trenv_attr in matches:
            # 발견된 매핑을 그대로 사용 (완전 자동화!)
            trenv_value = f'ka._TRENV.{trenv_attr}'
            
            # 소문자 버전 (함수 파라미터)
            dynamic_mappings[param_name] = trenv_value
            # 대문자 버전 (API 파라미터) 
            dynamic_mappings[param_name.upper()] = trenv_value
            
            discovered_mappings.append(f"{param_name}=xxx.{trenv_attr}")
        
        if discovered_mappings:
            print(f"[🎯자동발견] {len(discovered_mappings)}개 매핑: {', '.join(discovered_mappings)}")
            print(f"[🎯자동생성] {len(dynamic_mappings)}개 파라미터: {list(dynamic_mappings.keys())}")
        else:
            print("[🎯자동발견] .my_xxx 패턴 없음 - 조회성 API로 추정")
        
        
        return dynamic_mappings

    @classmethod
    def _modify_api_code(cls, api_code_path: str, params: Dict[str, Any], api_type: str) -> str:
        """API 코드 수정 (파라미터 적용)"""
        try:
            import re

            with open(api_code_path, 'r', encoding='utf-8') as f:
                code = f.read()

            # 1. sys.path.extend 관련 코드 제거
            code = re.sub(r"sys\.path\.extend\(\[.*?\]\)", "", code, flags=re.DOTALL)
            code = re.sub(r"import sys\n", "", code)  # import sys도 제거

            # 2. 코드에서 함수명과 시그니처 추출
            function_match = re.search(r'def\s+(\w+)\s*\((.*?)\):', code, re.DOTALL)
            if not function_match:
                raise Exception("코드에서 함수를 찾을 수 없습니다.")

            function_name = function_match.group(1)
            function_params = function_match.group(2)

            # 3. 함수가 max_depth 파라미터를 받는지 확인
            has_max_depth = 'max_depth' in function_params

            # 4. 파라미터 조정
            adjusted_params = params.copy()

            # max_depth 파라미터 처리
            if has_max_depth:
                # 함수가 max_depth를 받는 경우에만 처리
                if 'max_depth' not in adjusted_params:
                    adjusted_params['max_depth'] = 1
                    print(f"[기본값] {function_name} 함수에 max_depth=1 설정")
                else:
                    print(f"[사용자 설정] {function_name} 함수에 max_depth={adjusted_params['max_depth']} 사용")
            else:
                # 함수가 max_depth를 받지 않는 경우 제거
                if 'max_depth' in adjusted_params:
                    del adjusted_params['max_depth']
                    print(f"[제거] {function_name} 함수는 max_depth 파라미터를 지원하지 않아 제거함")

            # 🆕 동적으로 trenv 패턴 추출
            dynamic_mappings = cls._extract_trenv_params_from_example(code)
            
            # 기본 매핑과 동적 매핑 결합
            account_mappings = {
                'cano': 'ka._TRENV.my_acct',  # 종합계좌번호 (변수 접근)
                'acnt_prdt_cd': 'ka._TRENV.my_prod',  # 계좌상품코드 (변수 접근)
                'my_htsid': 'ka._TRENV.my_htsid',  # HTS ID (변수 접근)
                'user_id': 'ka._TRENV.my_htsid',  # domestic_stock에서 발견된 변형
                **dynamic_mappings  # 동적으로 발견된 매핑 추가
            }

            for param_name, correct_value in account_mappings.items():
                if param_name in function_params:
                    if param_name in adjusted_params:
                        original_value = adjusted_params[param_name]
                        adjusted_params[param_name] = correct_value
                        print(f"[보안강제] {function_name} 함수의 {param_name}='{original_value}' → {correct_value} (LLM값 무시)")
                    else:
                        adjusted_params[param_name] = correct_value
                        print(f"[자동설정] {function_name} 함수에 {param_name}={correct_value} 설정")

            # 거래소ID구분코드 처리 (API 타입 기반 추론)
            if 'excg_id_dvsn_cd' in function_params and 'excg_id_dvsn_cd' not in adjusted_params:
                if api_type.startswith('domestic'):
                    adjusted_params['excg_id_dvsn_cd'] = '"KRX"'
                    print(f"[추론] 국내 API({api_type})로 판단하여 excg_id_dvsn_cd='KRX' 설정")
                else:
                    print(f"[경고] {api_type} API에서 excg_id_dvsn_cd 파라미터가 필요합니다. (예: NASD, NYSE, KRX)")
                    # overseas_stock 등은 사용자가 명시적으로 제공해야 함

            # 5. 함수 호출 코드 생성 (ka.auth() - env_dv에 따라 분기)
            # env_dv 값에 따른 인증 방식 결정
            env_dv = params.get('env_dv', 'real')
            if env_dv == 'demo':
                auth_code = 'ka.auth("vps")'
                print(f"[모의투자] {function_name} 함수에 ka.auth(\"vps\") 적용")
            else:
                auth_code = 'ka.auth()'
                print(f"[실전투자] {function_name} 함수에 ka.auth() 적용")
            
            call_code = f"""
# API 함수 호출
if __name__ == "__main__":
    try:
        # 인증 초기화 (env_dv={env_dv})
        {auth_code}

        result = {function_name}({", ".join([f"{k}={v if isinstance(v, str) and v.startswith('ka._TRENV.') else repr(v)}" for k, v in adjusted_params.items()])})
    except TypeError as e:
        # 🚨 핵심 오류 메시지만 출력
        print(f"❌ TypeError: {{str(e)}}")
        print()
        
        # 파라미터 오류 처리 - LLM 교육용 메시지
        if 'stock_name' in {repr(list(params.keys()))}:
            print("💡 해결방법: find_stock_code로 종목을 검색하세요.")
        else:
            print("💡 해결방법: find_api_detail로 API 상세 정보를 확인하세요")
        import sys
        sys.exit(1)
    
    try:
        
        # N개 튜플 반환 함수 처리 (예: inquire_balance는 (df1, df2) 반환)
        if isinstance(result, tuple):
            # 튜플인 경우 - N개의 DataFrame 처리
            output = {{}}
            for i, item in enumerate(result):
                if hasattr(item, 'to_dict'):
                    # DataFrame인 경우
                    output[f"output{{i+1}}"] = item.to_dict('records') if not item.empty else []
                else:
                    # 일반 객체인 경우
                    output[f"output{{i+1}}"] = str(item)
            
            import json
            print(json.dumps(output, ensure_ascii=False, indent=2))
        elif hasattr(result, 'empty') and not result.empty:
            print(result.to_json(orient='records', force_ascii=False))
        elif isinstance(result, dict):
            import json
            print(json.dumps(result, ensure_ascii=False))
        elif isinstance(result, (list, tuple)):
            import json
            print(json.dumps(result, ensure_ascii=False))
        else:
            print(str(result))
    except Exception as e:
        print(f"오류 발생: {{str(e)}}")
"""

            # 6. 코드 끝에 함수 호출 추가
            modified_code = code + call_code

            # 7. 수정된 코드 저장
            with open(api_code_path, 'w', encoding='utf-8') as f:
                f.write(modified_code)

            return api_code_path
        except Exception as e:
            raise Exception(f"코드 수정 실패: {str(e)}")

    def _execute_code(self, temp_dir: str, timeout: int = 15) -> Dict[str, Any]:
        """코드 실행"""
        try:
            # 실행할 파일 경로 (상대 경로로 변경)
            api_code_path = "api_code.py"

            # subprocess로 코드 실행
            result = subprocess.run(
                [self.venv_python, api_code_path],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            if result.returncode == 0:
                # 성공 시 stdout을 결과로 반환
                return {
                    "success": True,
                    "output": result.stdout,
                    "error": result.stderr
                }
            else:
                # 실패 시 stderr와 stdout 모두 확인
                error_message = result.stderr if result.stderr else result.stdout
                return {
                    "success": False,
                    "output": result.stdout,
                    "error": error_message
                }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"실행 시간 초과 ({timeout}초)"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"실행 중 오류: {str(e)}"
            }

    def _cleanup_temp_directory(self, temp_dir: str):
        """임시 디렉토리 정리"""
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception as e:
            print(f"임시 디렉토리 정리 실패: {temp_dir}, 오류: {str(e)}")

    async def execute_api(self, ctx: Context, api_type: str, params: Dict[str, Any], github_url: str) -> Dict[str, Any]:
        """API 실행 메인 함수"""
        temp_dir = None
        start_time = time.time()

        try:
            await ctx.info(f"API 실행 시작: {api_type}")

            # 1. 임시 디렉토리 생성
            # FastMCP Context에서 request_id 안전하게 가져오기
            try:
                request_id = ctx.get_state(factory.CONTEXT_REQUEST_ID)
            except:
                request_id = "unknown"
            temp_dir = self._create_temp_directory(request_id)

            # 2. kis_auth.py 다운로드
            if not self._download_kis_auth(temp_dir):
                raise Exception("kis_auth.py 다운로드 실패")

            # 3. API 코드 다운로드
            api_code_path = self._download_api_code(github_url, temp_dir, api_type)

            # 4. 코드 수정
            self._modify_api_code(api_code_path, params, api_type)

            # 5. 코드 실행
            execution_result = self._execute_code(temp_dir)

            # 6. 실행 시간 계산
            execution_time = time.time() - start_time

            # 7. 결과 반환
            result = {
                "success": execution_result["success"],
                "api_type": api_type,
                "params": params,
                "message": f"{self.tool_name} API 호출 완료",
                "execution_time": f"{execution_time:.2f}s",
                "temp_dir": temp_dir,
                "venv_used": True,
                "cleanup_success": True
            }

            if execution_result["success"]:
                result["data"] = execution_result["output"]
            else:
                result["error"] = execution_result["error"]

            return result

        except Exception as e:
            await ctx.error(f"API 실행 중 오류: {str(e)}")
            return {
                "success": False,
                "api_type": api_type,
                "params": params,
                "error": str(e),
                "execution_time": f"{time.time() - start_time:.2f}s",
                "temp_dir": temp_dir,
                "venv_used": True,
                "cleanup_success": False
            }
        finally:
            # 8. 임시 디렉토리 정리
            if temp_dir:
                self._cleanup_temp_directory(temp_dir)


class BaseTool(ABC):
    """MCP 도구 기본 클래스"""

    def __init__(self):
        """도구 초기화"""
        self._load_config()
        self.api_executor = ApiExecutor(self.tool_name)
        self.master_file_manager = MasterFileManager(self.tool_name)
        self.db = Database()

    # ========== Abstract Properties ==========
    @property
    @abstractmethod
    def tool_name(self) -> str:
        """도구 이름 (하위 클래스에서 구현 필수)"""
        pass

    # ========== Public Properties ==========
    @property
    def description(self) -> str:
        """도구 설명 (분류.json에서 동적 생성)"""
        return self._generate_description()

    @property
    def config_file(self) -> str:
        """JSON 설정 파일 경로 (tool_name 기반 자동 생성)"""
        return f"./configs/{self.tool_name}.json"

    # ========== Public Methods ==========
    def register(self, mcp_server: FastMCP) -> None:
        """MCP 서버에 도구 등록"""
        mcp_server.tool(
            self._run,
            name=self.tool_name,
            description=self.description,
        )

    # ========== Protected Methods ==========
    def _load_config(self) -> None:
        """JSON 설정 파일 로드"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            # 임시로 빈 설정으로 초기화
            self.config = {"apis": {}}

    def _generate_description(self) -> str:
        """분류.json에서 도구 설명 동적 생성"""
        try:
            config_json_path = f"./configs/{self.tool_name}.json"
            with open(config_json_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)

            tool_info = config_data.get("tool_info")
            apis = config_data.get("apis", {})

            if not tool_info:
                return f"{self.tool_name} 도구의 tool_info가 없습니다."

            # description 문자열 구성
            lines = [tool_info.get("introduce", "")]

            # introduce_append가 있으면 추가
            introduce_append = tool_info.get("introduce_append", "").strip()
            if introduce_append:
                lines.append(introduce_append)

            lines.append("")  # 빈 줄
            lines.append("[지원 기능]")

            # API 목록 추가
            for api_type, api_info in apis.items():
                lines.append(f"- {api_info['name']} (api_type: \"{api_type}\")")

            lines.append("")  # 빈 줄

            # 개선된 구조 적용
            lines.append("📋 사용 방법:")
            lines.append("1. find_api_detail로 API 상세 정보를 확인하세요")
            lines.append("2. api_type을 선택하고 params에 필요한 파라미터를 입력하세요")
            lines.append("3. 종목명으로 검색할 경우: stock_name='종목명' 파라미터를 사용하세요")
            lines.append("4. 모의투자 시에는 env_dv='demo'를 추가하세요")
            lines.append("")
            lines.append("🔧 특별한 api_type 및 예시:")
            lines.append(f"- find_stock_code (종목번호 검색) : {self.tool_name}({{ \"api_type\": \"find_stock_code\", \"params\": {{ \"stock_name\": \"삼성전자\" }} }})")
            lines.append(f"- find_api_detail (API 정보 조회) : {self.tool_name}({{ \"api_type\": \"find_api_detail\", \"params\": {{ \"api_type\": \"inquire_price\" }} }})")
            lines.append("")
            lines.append("🔍 종목명 사용: stock_name=\"삼성전자\" → 자동으로 종목번호 변환하여 실행")
            lines.append(f"{self.tool_name}({{ \"api_type\": \"inquire_price\", \"params\": {{ \"stock_name\": \"삼성전자\" }} }})")
            lines.append("")
            lines.append("💡 주요 파라미터:")
            if self.tool_name.startswith('domestic'):
                lines.append("- 시장코드(fid_cond_mrkt_div_code)='J'(KRX)/'NX'(넥스트레이드)/'UN'(통합)")
            lines.append("- 매매구분(ord_dv)='buy'(매수)/'sell'(매도)")
            lines.append("- 실전모의구분(env_dv)='real'(실전)/'demo'(모의)")
            lines.append("")
            lines.append("⚠️ 중요: API 호출 시 필수 주의사항")
            lines.append("**API 실행 전 반드시 API 상세 문서의 파라미터를 확인하세요. Request Query Params와 Request Body 입력 시 추측이나 과거 실행 값 사용 금지, 확인된 API 상세 문서의 값을 사용하세요.**")
            lines.append("**파라미터 description에 '공란'이 있는 경우 기본적으로 빈값으로 처리하되, 아닌 경우에는 값을 넣어도 됩니다.**")
            lines.append("**🎯 모의투자 관련: 사용자가 '모의', '모의투자', '데모', '테스트' 등의 용어를 언급하거나 모의투자 관련 요청을 할 경우, 반드시 env_dv 파라미터를 'demo'로 설정하여 API를 호출해야 합니다. env_dv 파라미터가 있는 모든 API에서 모의투자 시에는 env_dv='demo', 실전투자 시에는 env_dv='real'을 사용합니다. 기본값은 'real'이므로 모의투자 요청 시 반드시 env_dv='demo'를 명시적으로 설정해주세요.**")
            lines.append("")
            lines.append("🔒 자동 처리되는 파라미터 (제공하지 마세요):")
            lines.append("• cano (계좌번호), acnt_prdt_cd (계좌상품코드), my_htsid (HTS ID) - 시스템 자동 설정")
            if self.tool_name.startswith('domestic'):
                lines.append("• excg_id_dvsn_cd (거래소구분) - 국내 API는 자동으로 KRX 설정")
            lines.append("")

            # 예시 호출 추가
            examples = tool_info.get("examples", [])
            if examples:
                lines.append("💻 예시 호출:")
                for example in examples:
                    params_str = json.dumps(example.get('params', {}), ensure_ascii=False)
                    lines.append(
                        f"{self.tool_name}({{ \"api_type\": \"{example['api_type']}\",\"params\": {params_str} }})")

            return "\n".join(lines)

        except Exception as e:
            return f"{self.tool_name} 도구 설명 생성 중 오류: {str(e)}"

    async def _run(self, ctx: Context, api_type: str, params: dict) -> Dict[str, Any]:
        """공통 실행 로직"""
        try:
            await ctx.info(f"{self.tool_name} running with api_type: {api_type}")

            # 1) 인자 구조 검증(가볍게)
            if not api_type or not isinstance(params, dict):
                return {
                    "ok": False,
                    "error": "MISSING_OR_INVALID_ARGS",
                    "missing": [k for k in ("api_type", "params") if
                                not (api_type if k == "api_type" else isinstance(params, dict))],
                    "invalid": [] if isinstance(params, dict) else [{"field": "params", "expected": "object"}],
                }

            # 2. 특별한 api_type 처리
            if api_type == "find_stock_code":
                return await self._handle_find_stock_code(ctx, params)
            elif api_type == "find_api_detail":
                return await self._handle_find_api_detail(ctx, params)
            
            # 3. API 설정 조회
            if api_type not in self.config['apis']:
                return {"ok": False, "error": f"지원하지 않는 API 타입: {api_type}"}


            # 4. 종목명 자동 처리 (stock_name이 있으면 자동으로 pdno 변환)
            params = await self._process_stock_name(ctx, params)
            
            # 5. 실제 실행 (래핑 함수 선택 → OPEN API 호출)
            data = await self._run_api(ctx, api_type, params)
            return {"ok": True, "data": data}

        except Exception as e:
            await ctx.error(f"실행 중 오류: {str(e)}")
            return {"ok": False, "error": str(e)}


    async def _run_api(self, ctx: Context, api_type: str, params: Dict[str, Any]) -> Any:
        """API 실행 - ApiExecutor 사용"""
        try:
            api_info = self.config['apis'][api_type]
            github_url = api_info.get('github_url')

            if not github_url:
                return {"error": f"GitHub URL이 없습니다: {api_type}"}

            # ApiExecutor를 사용하여 API 실행
            result = await self.api_executor.execute_api(
                ctx=ctx,
                api_type=api_type,
                params=params,
                github_url=github_url
            )

            return result

        except Exception as e:
            return {"error": f"API 실행 중 오류: {str(e)}"}
    
    async def _process_stock_name(self, ctx: Context, params: Dict[str, Any]) -> Dict[str, Any]:
        """종목명/종목코드 자동 처리 (stock_name이 있으면 자동으로 pdno 변환)"""
        try:
            # 종목명으로 찾을 수 있는 파라미터들
            stock_name_params = ["stock_name", "stock_name_kr", "korean_name", "company_name"]
            
            # 파라미터에서 종목명/종목코드 찾기
            search_value = None
            for param_name in stock_name_params:
                if param_name in params and params[param_name]:
                    search_value = params[param_name]
                    break
            
            # 검색할 값이 없으면 그대로 반환
            if not search_value:
                return params
            
            await ctx.info(f"검색값 발견: {search_value}, 자동 검색 시작")
            
            # 종목명 또는 종목코드로 검색
            result = await self._find_stock_by_name_or_code(ctx, search_value)
            
            if result["found"]:
                params["pdno"] = result["code"]
                await ctx.info(f"종목번호 자동 찾기 성공: {search_value} → {result['code']}")
                # 원본 검색값 보존
                params["_original_search_value"] = search_value
                params["_resolved_stock_code"] = result["code"]
            else:
                await ctx.warning(f"종목을 찾을 수 없음: {search_value}")
                # 종목을 찾지 못해도 원본 파라미터 유지
            
            return params
            
        except Exception as e:
            await ctx.error(f"종목명 자동 처리 실패: {str(e)}")
            return params
    
    async def _find_stock_by_name_or_code(self, ctx: Context, search_value: str) -> Dict[str, Any]:
        """종목명 또는 종목코드로 종목번호 찾기"""
        try:
            # 검색어에서 띄어쓰기 제거
            search_term = search_value.replace(" ", "")
            
            # 데이터베이스 연결 확인
            if not self.db.ensure_initialized():
                return {"found": False, "message": "데이터베이스 초기화 실패"}

            # 마스터 파일 업데이트 확인 (force_update=False로 필요시에만 업데이트)
            try:
                from module.plugin import MasterFileManager
                master_file_manager = MasterFileManager(self.tool_name)
                await master_file_manager.ensure_master_file_updated(ctx, force_update=False)
            except Exception as e:
                await ctx.warning(f"마스터 파일 업데이트 확인 중 오류: {str(e)}")
            
            # DB 엔진
            db_engine = self.db.get_by_name("master")
            master_models = MasterFileManager.get_master_models_for_tool(self.tool_name)
            
            if not master_models:
                return {"found": False, "message": f"지원하지 않는 툴: {self.tool_name}"}
            
            # 각 모델에서 우선순위별 검색
            for model_class in master_models:
                try:
                    # 1순위: 종목코드로 완전 매칭
                    code_results = db_engine.list(
                        model_class, 
                        filters={"code": search_term}, 
                        limit=1
                    )
                    
                    if code_results:
                        result = code_results[0]
                        return {
                            "found": True,
                            "code": result.code,
                            "name": result.name,
                            "ex": result.ex if hasattr(result, 'ex') else None,
                            "match_type": "code_exact"
                        }
                    
                    # 2순위: 종목명으로 완전 매칭
                    name_results = db_engine.list(
                        model_class, 
                        filters={"name": search_term}, 
                        limit=1
                    )
                    
                    if name_results:
                        result = name_results[0]
                        return {
                            "found": True,
                            "code": result.code,
                            "name": result.name,
                            "ex": result.ex if hasattr(result, 'ex') else None,
                            "match_type": "name_exact"
                        }
                    
                    # 3순위: 종목명으로 앞글자 매칭
                    prefix_results = db_engine.list(
                        model_class, 
                        filters={"name": f"{search_term}%"}, 
                        limit=1
                    )
                    
                    if prefix_results:
                        result = prefix_results[0]
                        return {
                            "found": True,
                            "code": result.code,
                            "name": result.name,
                            "ex": result.ex if hasattr(result, 'ex') else None,
                            "match_type": "name_prefix"
                        }
                    
                    # 4순위: 종목명으로 중간 매칭
                    contains_results = db_engine.list(
                        model_class, 
                        filters={"name": f"%{search_term}%"}, 
                        limit=1
                    )
                    
                    if contains_results:
                        result = contains_results[0]
                        return {
                            "found": True,
                            "code": result.code,
                            "name": result.name,
                            "ex": result.ex if hasattr(result, 'ex') else None,
                            "match_type": "name_contains"
                        }
                        
                except Exception as e:
                    continue
            
            return {"found": False, "message": f"종목을 찾을 수 없음: {search_value}"}
            
        except Exception as e:
            return {"found": False, "message": f"종목 검색 오류: {str(e)}"}
    
    def get_api_info(self, api_type: str) -> Dict[str, Any]:
        """API 정보 조회 (리소스 기능 통합)"""
        try:
            # API 설정 조회
            if api_type not in self.config['apis']:
                return {
                    "error": f"지원하지 않는 API 타입: {api_type}",
                    "available_apis": list(self.config['apis'].keys()),
                    "api_type": api_type
                }
            
            # API 정보 반환
            api_info = self.config['apis'][api_type]
            
            # 파라미터 정보 정리
            params = api_info.get("params", {})
            param_details = {}
            
            for param_name, param_info in params.items():
                param_details[param_name] = {
                    "name": param_info.get("name", param_name),
                    "type": param_info.get("type", "str"),
                    "required": param_info.get("required", False),
                    "default_value": param_info.get("default_value"),
                    "description": param_info.get("description", "")
                }
            
            result = {
                "tool_name": self.tool_name,
                "api_type": api_type,
                "name": api_info.get("name", ""),
                "category_detail": api_info.get("category", ""),
                "method": api_info.get("method", ""),
                "api_path": api_info.get("api_path", ""),
                "github_url": api_info.get("github_url", ""),
                "params": param_details
            }
            
            return result
            
        except Exception as e:
            return {
                "error": f"API 정보 조회 중 오류 발생: {str(e)}",
                "tool_name": self.tool_name,
                "api_type": api_type
            }
    
    async def _handle_find_stock_code(self, ctx: Context, params: Dict[str, Any]) -> Dict[str, Any]:
        """종목 검색 처리"""
        try:
            await ctx.info(f"종목 검색 요청: {self.tool_name}")
            
            # stock_name 파라미터 확인
            search_value = params.get("stock_name")
            if not search_value:
                return {
                    "ok": False,
                    "error": "MISSING_OR_INVALID_ARGS",
                    "missing": ["stock_name"],
                    "message": "stock_name 파라미터가 필요합니다. (종목명 또는 종목코드 입력 가능)"
                }
            
            # 종목 검색 실행 (종목명 또는 종목코드)
            result = await self._find_stock_by_name_or_code(ctx, search_value)
            
            if result["found"]:
                return {
                    "ok": True,
                    "data": {
                        "tool_name": self.tool_name,
                        "search_value": search_value,
                        "found": True,
                        "stock_code": result["code"],
                        "stock_name_found": result["name"],
                        "ex": result.get("ex"),
                        "match_type": result.get("match_type"),
                        "message": f"'{search_value}' 종목을 찾았습니다. 종목번호: {result['code']}",
                        "usage_guide": f"find_api_detail로 API상세정보를 확인하고 종목코드 '{result['code']}'를 해당 API의 종목코드 필드에 입력하여 실행하세요.",
                        "next_step": f"{self.tool_name} 툴에서 find_api_detail로 확인한 종목코드 필드에 '{result['code']}'를 입력하세요."
                    }
                }
            else:
                return {
                    "ok": False,
                    "error": "STOCK_NOT_FOUND",
                    "message": f"'{search_value}' 종목을 찾을 수 없습니다.",
                    "suggestions": [
                        "종목명의 철자가 정확한지 확인",
                        "종목코드가 정확한지 확인",
                        "띄어쓰기나 특수문자가 있는지 확인",
                        "다른 검색어로 시도 (예: '삼성전자' 대신 '삼성' 또는 '005930')"
                    ]
                }
                
        except Exception as e:
            await ctx.error(f"종목 검색 처리 중 오류: {str(e)}")
            return {"ok": False, "error": str(e)}
    
    async def _handle_find_api_detail(self, ctx: Context, params: Dict[str, Any]) -> Dict[str, Any]:
        """API 상세 정보 조회 처리"""
        try:
            await ctx.info(f"API 상세 정보 조회 요청: {self.tool_name}")
            
            # api_type 파라미터 확인
            target_api_type = params.get("api_type")
            if not target_api_type:
                return {
                    "ok": False,
                    "error": "MISSING_OR_INVALID_ARGS",
                    "missing": ["api_type"],
                    "message": "api_type 파라미터가 필요합니다.",
                    "available_apis": list(self.config['apis'].keys())
                }
            
            # API 정보 조회
            api_info = self.get_api_info(target_api_type)
            
            if "error" in api_info:
                return {
                    "ok": False,
                    "error": api_info["error"],
                    "available_apis": api_info.get("available_apis", [])
                }
            
            return {
                "ok": True,
                "data": api_info
            }
                
        except Exception as e:
            await ctx.error(f"API 상세 정보 조회 처리 중 오류: {str(e)}")
            return {"ok": False, "error": str(e)}
