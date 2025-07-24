using System.Data;
using System.Text;
using YamlDotNet.Serialization;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using System;
using System.Linq;
using System.Threading.Tasks;




namespace KIS_Common {
    class Common
    {
        private static string configRoot = @"d:\KIS\config\";
        private static string tokenTmp = configRoot + "KIS" + DateTime.Now.ToString("yyyyMMdd");
        private static Dictionary<string, string> _cfg;
        public static (string my_app, string my_sec , string my_acct, string my_prod, string my_token, string my_url) _TRENV;
        private static DateTime _lastAuthTime;
        private static bool _DEBUG = false;
        public static bool _isPaper = false;
        private static Dictionary<string, string> _baseHeaders;
        private static string _mode = "prod";
        public static int _rescode;
        public static HttpResponseMessage _resp;
        public static Dictionary<string, string> _header;
        public static Dictionary<string, object> _body;
        public static string _errCode;
        public static string _errMessage;

        public static async Task doAuth(String mode)
        {
            if (!File.Exists(tokenTmp)){
                File.Create(tokenTmp).Close();
            }
            using (var reader = new StreamReader(configRoot + "kis_devlp.yaml", Encoding.UTF8)){
                var deserializer = new Deserializer();
                _cfg = deserializer.Deserialize<Dictionary<string, string>>(reader);
            }
            _baseHeaders = new Dictionary<string, string>{
                { "Content-Type", "application/json" },
                { "Accept", "text/plain" },
                { "charset", "UTF-8" },
                { "User-Agent", _cfg["my_agent"] }
            };

            if(mode.Equals("V")) {
                _DEBUG = true;
                _mode = "vps";
                await Auth(_mode, _cfg["my_prod"]);
            }
            else if(mode.Equals("D")) {
                _DEBUG = true;
                _mode = "dev";
                await Auth(_mode, _cfg["my_prod"]);
            }
            else {
                _DEBUG = false;
                _mode = "prod";
                await Auth(_mode, _cfg["my_prod"]);
            }
        }

        private static void SaveToken(string myToken, string myExpired, string mode)
        {

            Console.WriteLine("===== Exp " + myExpired);

            using (var writer = new StreamWriter(tokenTmp, false, Encoding.UTF8))
            {
                writer.WriteLine($"token; {myToken}");
                writer.WriteLine($"valid-date; {myExpired}");
                writer.Write($"mode; {mode}");
            }
        }

        private static string? ReadToken()
        {
            try
            {
                var lines = File.ReadAllLines(tokenTmp, Encoding.UTF8);
                var tokenData = lines.Select(line => line.Split(';')).ToDictionary(parts => parts[0].Trim(), parts => parts[1].Trim());

                string expDt = DateTime.Parse(tokenData["valid-date"]).ToString("yyyy-MM-dd HH:mm:ss");
                string nowDt = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss");
                string getMode = tokenData["mode"];
                Console.WriteLine("Mode : " + getMode);

                if (string.Compare(expDt, nowDt) > 0 && _mode.Equals(getMode)){
                    return tokenData["token"];
                }
                else{
                    return null;
                }
            }
            catch
            {
                return null;
            }
        }

        private static Dictionary<string, string> GetBaseHeader()
        {
            DateTime n2 = DateTime.Now;
            if ((n2 - _lastAuthTime).TotalSeconds >= 86400){
                ReAuth(_mode, _cfg["my_prod"]);
            }
            return new Dictionary<string, string>(_baseHeaders);
        }

        private static (string my_app, string my_sec , string my_acct, string my_prod, string my_token, string my_url) GetTRENV()
        {
            return _TRENV;
        }

        public static void SetTRENV(Dictionary<string, string> cfg)
        {
            _TRENV = (cfg["my_app"],cfg["my_sec"],cfg["my_acct"],cfg["my_prod"],cfg["my_token"],cfg["my_url"]);
        }

        private static void ChangeTREnv(string tokenKey, string svr, string product)
        {
            var cfg = new Dictionary<string, string>();
            if (svr == "prod")
            {
                cfg["my_app"] = _cfg["my_app"];
                cfg["my_sec"] = _cfg["my_sec"];
                cfg["my_acct"] = _cfg["my_acct"];
                _isPaper = false;
            }
            else if (svr == "vps")
            {
                cfg["my_app"] = _cfg["paper_app"];
                cfg["my_sec"] = _cfg["paper_sec"];
                cfg["my_acct"] = _cfg["paper_acct"];
                _isPaper = true;
            }
            else {
                cfg["my_app"] = _cfg["dev_app"];
                cfg["my_sec"] = _cfg["dev_sec"];
                cfg["my_acct"] = _cfg["dev_acct"];
                _isPaper = false;
            }

            cfg["my_prod"] = product;
            cfg["my_token"] = tokenKey;
            cfg["my_url"] = _cfg[svr];

            SetTRENV(cfg);
        }

        private static async Task<string?>Auth(string svr, string product)
        {
            var p = new Dictionary<string, string>{
                { "grant_type", "client_credentials" }
            };

            string ak1 = svr == "prod" ? "my_app" : (svr == "vps" ? "paper_app" : "dev_app");
            string ak2 = svr == "prod" ? "my_sec" : (svr == "vps" ? "paper_sec" : "dev_sec");

            p["appkey"] = _cfg[ak1];
            p["appsecret"] = _cfg[ak2];

            string savedToken = ReadToken();
            if (savedToken == null){
                var url = $"{_cfg[svr]}/oauth2/tokenP";
                var client = new HttpClient();
                var request = new HttpRequestMessage(HttpMethod.Post, url);
                request.Content = new StringContent(JsonConvert.SerializeObject(p), Encoding.UTF8, "application/json");
                var response = client.SendAsync(request).Result;
                if (response.IsSuccessStatusCode){
                    var jsonData = JsonConvert.DeserializeObject<Dictionary<string, string>>(await response.Content.ReadAsStringAsync());
                    string myToken = jsonData["access_token"];
                    string myExpired = jsonData["access_token_token_expired"];
                    SaveToken(myToken, myExpired, svr);
                    savedToken = ReadToken();
                    ChangeTREnv($"Bearer {savedToken}", svr, product);
                }
                else{
                    Console.WriteLine("Get Authentication token fail!\nYou have to restart your app!!!");
                    return null;
                }
            }
            else{
                ChangeTREnv($"Bearer {savedToken}", svr, product);
            }

            _baseHeaders["authorization"] = _TRENV.Item5;
            _baseHeaders["appkey"] = _TRENV.Item1;
            _baseHeaders["appsecret"] = _TRENV.Item2;

            _lastAuthTime = DateTime.Now;

            if (_DEBUG)
            {
                Console.WriteLine($"[{_lastAuthTime}] => get AUTH Key completed!");
            }

            return null;
        }

        private static async void ReAuth(string svr, string product)
        {
            await Auth(svr, product);
        }

        private static Dictionary<string, string> GetEnv()
        {
            return _cfg;
        }

        public static (string my_app, string my_sec , string my_acct, string my_prod, string my_token, string my_url) GetTREnv()
        {
            return _TRENV;
        }

        private static async Task SetOrderHashKey(Dictionary<string, string> h, Dictionary<string, string> p)
        {
            string url = $"{GetTREnv().my_url}/uapi/hashkey";

            using (var client = new HttpClient())
            {
                var content = new StringContent(JsonConvert.SerializeObject(p), Encoding.UTF8, "application/json");
                var response = await client.PostAsync(url, content);
                if (response.IsSuccessStatusCode)
                {
                    var jsonData = JsonConvert.DeserializeObject<Dictionary<string, string>>(await response.Content.ReadAsStringAsync());
                    h["hashkey"] = jsonData["HASH"];
                }
                else
                {
                    Console.WriteLine("Error: " + response.StatusCode);
                }
            }
        }

        private static bool IsPaperTrading()
        {
            return _isPaper;
        }

        // 응답값 사용을 위한 변수 세팅 메서드
        public static void SetAPIRespVal(HttpResponseMessage resp)
        {
            _rescode = (int)resp.StatusCode;
            _resp = resp;
            _header = _SetHeader();
            _body = _SetBody();
            _errCode = (string)_body["msg_cd"];
            _errMessage = (string)_body["msg1"];
        }

        // 응답코드 리턴값
        public int GetResCode()
        {
            return _rescode;
        }
        
        // 응답메시지 리턴값
        public HttpResponseMessage GetResponse()
        {
            return _resp;
        }

        // 트랜잭션 에러코드 리턴값
        public string GetErrorCode()
        {
            return _errCode;
        }

        // 트랜잭션 에러메시지 리턴값
        public string GetErrorMessage()
        {
            return _errMessage;
        }

        // 헤더 지정
        private static Dictionary<string, string> _SetHeader()
        {
            return _resp.Headers.ToDictionary(x => x.Key.ToLower(), x => string.Join(", ", x.Value));
        }

        // 헤더 수신
        public Dictionary<string, string> GetHeader()
        {
            return _header;
        }

        // 바디 지정
        private static Dictionary<string, object> _SetBody()
        {
            return JsonConvert.DeserializeObject<Dictionary<string, object>>(_resp.Content.ReadAsStringAsync().Result);

        }

        // 바디 수신
        public Dictionary<string, object> GetBody()
        {
            return _body;
        }

        // 트랜잭션 정상여부 확인 부울 값
        public bool IsOK()
        {
            return (string) _body["rt_cd"] == "0";
        }

        // 디버그 출력용
        public static void PrintAll()
        {
            Common ka = new Common();
            Console.WriteLine("<Header>");
            foreach (var x in ka.GetHeader().Keys)
            {
                Console.WriteLine($"\t-{x}: {ka.GetHeader()[x]}");
            }
            Console.WriteLine("<Body>");
            foreach (var x in ka.GetBody().Keys)
            {
                Console.WriteLine($"\t-{x}: {ka.GetBody()[x]}");
            }
        }

        // 에러 메시지 출력용
        public void PrintError(string url)
        {
            Console.WriteLine("-------------------------------\nError in response: " + GetResCode() + " url=" + url);
            Console.WriteLine("rt_cd : " + GetBody()["rt_cd"] + " / msg_cd : " + GetErrorCode() + " / msg1 : " + GetErrorMessage());
            Console.WriteLine("-------------------------------");
        }
    
       // 특정 JToken 결과값을 DataTable로 변환하는 메서드
       public static DataTable ConvertToDataTable(JToken? data){

            DataTable dataTable = new DataTable();
            JArray jArray = new JArray();
            if (data is null) {
                Console.WriteLine("조회 값 없음");
                return null;
            }
            else {
                Console.WriteLine("Return Type : " + data.Type.ToString());
            }
            if (data.Type.ToString().Equals("Array")) {
                jArray = (JArray) data;
            }
            else {
                jArray.Add(data);
            }            
            
            if (jArray.Count > 0)
            {
                // Add columns to DataTable
                foreach (var firstRow in jArray.Children<JObject>())
                {
                    foreach (var property in firstRow.Properties())
                    {
                        if (!dataTable.Columns.Contains(property.Name))
                        {
                            dataTable.Columns.Add(property.Name);
                        }
                    }
                    break; 
                }

                // Add rows to DataTable
                foreach (var row in jArray.Children<JObject>())
                {
                    DataRow dataRow = dataTable.NewRow();
                    foreach (var property in row.Properties())
                    {
                        dataRow[property.Name] = property.Value.ToString();
                    }
                    dataTable.Rows.Add(dataRow);
                }
            }

            return dataTable;
        }

        // JObject 결과값을 DataTable로 변환하는 메서드
        public static DataTable ConvertToDataTable(JObject data)
        {

            var dataTable = new DataTable();
            Console.WriteLine("Return Type : " + data.Type.ToString());

            foreach (var property in data.Properties())
            {
                dataTable.Columns.Add(property.Name);
            }

            var row = dataTable.NewRow();
            foreach (var property in data.Properties())
            {
                row[property.Name] = property.Value;
            }

            dataTable.Rows.Add(row);

            return dataTable;
        }


        // DataTable 출력용
        public static void PrintDataTable(DataTable dataTable)
        {
            string line = "";
            foreach (DataColumn item in dataTable.Columns)
            {
                line += item.ColumnName +"   ";
            }
            line += "\n";
            foreach (DataRow row in dataTable.Rows)
            {
                for (int i = 0; i < dataTable.Columns.Count; i++)
                {
                    line += row[i].ToString() + "   ";
                }
                line += "\n";
            }
            Console.WriteLine("==============================================================================");
            Console.WriteLine(line) ;
        }

        // API 호출 및 응답값 회신
        public static Task<HttpResponseMessage> UrlFetch(Dictionary<string, object> paramsDict, string apiUrl = "", string ptrId = "", string trCont = "", Dictionary<string, string>? appendHeaders = null, bool postFlag = true , bool hashFlag = false)
        {
            // 요청 URL
            string url = $"{GetTREnv().my_url}{apiUrl}";

            // HTTPClient 사용, RestSharp 사용 시 별도 코드 변환 필요
            var client = new HttpClient();
            HttpResponseMessage resp = new HttpResponseMessage();

            // 최대 타임아웃 설정 → 기본 100ms, 네트워크 상황에 따라 TimeSpan으로 타임아웃 시간 설정
            client.Timeout = TimeSpan.FromMinutes(10);          

            // 요청 헤더 설정
            var headers = GetBaseHeader(); 
            string trId = ptrId;
            if (IsPaperTrading()){ //모의투자인 경우, 트랜잭션 ID 앞에 'V'가 붙음
                if (ptrId[0] == 'T' || ptrId[0] == 'J' || ptrId[0] == 'C'){
                 trId = "V" + ptrId.Substring(1);
                }
            }
            headers["tr_id"] = trId;
            headers["custtype"] = "P";
            headers["tr_cont"] = trCont;
            if (appendHeaders != null && appendHeaders.Count > 0)
            {
                foreach (var x in appendHeaders.Keys)
                {
                    headers[x] = appendHeaders[x];
                }
            }
            // 클라이언트 요청 헤더 값에 최종 설정
            foreach (var x in headers) {
                client.DefaultRequestHeaders.TryAddWithoutValidation(x.Key , x.Value);
            }

            // 디버그 기능 사용 시, 출력용
            
            if (_DEBUG)
            {
                Console.WriteLine("< Sending Info >");
                Console.WriteLine($"URL: {url}, TR: {trId}");
                Console.WriteLine($"<header>\n{string.Join(", ", headers.Select(h => $"{h.Key}: {h.Value}"))}");
                Console.WriteLine($"<body>\n{string.Join(", ", paramsDict.Select(p => $"{p.Key}: {p.Value}"))}");
            }
            

            // POST 방식, GET 방식에 따른 분기
            if (postFlag){
                resp = client.PostAsync(url, new StringContent(JsonConvert.SerializeObject(paramsDict), Encoding.UTF8, "application/json")).ConfigureAwait(false).GetAwaiter().GetResult();            
            } 
            else{
                resp = client.GetAsync(url + "?" + string.Join("&", paramsDict.Select(p => $"{p.Key}={p.Value}"))).ConfigureAwait(false).GetAwaiter().GetResult(); 
            }
            
            // 응답코드가 성공으로 나온 경우 결과 값을 최종 설정함. 오류인 경우에는 오류코드와 메시지 출력
            if (resp.IsSuccessStatusCode){
                SetAPIRespVal(resp); 
                if (_DEBUG) { PrintAll(); }
            }
            else{
                Console.WriteLine("Error Code : " + (int)resp.StatusCode + " | " + resp.Content);
            }

             return Task.FromResult(resp);

        }   
    }

   


}