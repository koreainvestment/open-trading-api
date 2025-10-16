unit MainForm;

interface

uses
  Winapi.Windows, Winapi.Messages, System.SysUtils, System.Classes, System.JSON,
  Vcl.Forms, Vcl.Controls, Vcl.StdCtrls, Vcl.Dialogs,
  sgcWebSocket, sgcWebSocket_Classes, sgcWebSocket_Client, sgcBase_Classes,
  sgcSocket_Classes, sgcTCP_Classes, sgcWebSocket_Classes_Indy;

type
  TForm1 = class(TForm)
    sgcWebSocketClient1: TsgcWebSocketClient;
    btnConnect: TButton;
    btnSubscribe: TButton;
    btnUnsubscribe: TButton;
    btnDisconnect: TButton;
    Memo1: TMemo;
    edtApprovalKey: TEdit;
    edtTrId: TEdit;
    edtTrKey: TEdit;
    Label1: TLabel;
    Label2: TLabel;
    Label3: TLabel;
    procedure btnConnectClick(Sender: TObject);
    procedure btnSubscribeClick(Sender: TObject);
    procedure btnUnsubscribeClick(Sender: TObject);
    procedure btnDisconnectClick(Sender: TObject);
    procedure sgcWebSocketClient1Connect(Connection: TsgcWSConnection);
    procedure sgcWebSocketClient1Disconnect(Connection: TsgcWSConnection; Code: Integer);
    procedure sgcWebSocketClient1Message(Connection: TsgcWSConnection; const Text: string);
    procedure sgcWebSocketClient1Error(Connection: TsgcWSConnection; const Error: string);
    procedure FormCreate(Sender: TObject);
    procedure edtTrIdChange(Sender: TObject);
  private
    APPROVAL_KEY: string;
    procedure LogMessage(const Msg: string);
    procedure SendSubscription(const TrType: string);
    procedure UpdateWebSocketURL;
  public
  end;

var
  Form1: TForm1;

implementation

{$R *.dfm}

procedure TForm1.FormCreate(Sender: TObject);
begin
  // 웹소켓 초기 설정
  sgcWebSocketClient1.Active := False;
  sgcWebSocketClient1.HeartBeat.Enabled := True;
  sgcWebSocketClient1.HeartBeat.Interval := 30000;
  
  btnSubscribe.Enabled := False;
  btnUnsubscribe.Enabled := False;
  btnDisconnect.Enabled := False;
  
  Memo1.Clear;
  
  // 기본값 설정
  edtTrId.Text := 'H0STCNT0';      // 국내주식 체결통보
  edtTrKey.Text := '005930';       // 삼성전자
  
  // URL 초기 설정
  UpdateWebSocketURL;
  
  LogMessage('═══════════════════════════════════════════');
  LogMessage('  한국투자증권 웹소켓 클라이언트 v1.0');
  LogMessage('═══════════════════════════════════════════');
  LogMessage('');
  LogMessage('[TR_ID 예시]');
  LogMessage('  H0STCNT0 : 국내주식 체결가');
  LogMessage('  H0STASP0 : 국내주식 호가');
  LogMessage('  HDFSCNT0 : 해외주식 지연체결가');
  LogMessage('  HDFSASP0 : 해외주식 호가');
  LogMessage('');
  LogMessage('[종목코드 예시]');
  LogMessage('  국내: 005930 (삼성전자), 000660 (SK하이닉스)');
  LogMessage('  해외: DNASTSLA (나스닥 테슬라), DNYSBABA (뉴욕 알리바바)');
  LogMessage('═══════════════════════════════════════════');
end;

procedure TForm1.UpdateWebSocketURL;
var
  trId: string;
begin
  trId := Trim(edtTrId.Text);
  if trId <> '' then
  begin
    sgcWebSocketClient1.URL := 'ws://ops.koreainvestment.com:21000/tryitout/' + trId;
    LogMessage('URL 업데이트: ws://ops.koreainvestment.com:21000/tryitout/' + trId);
  end;
end;

procedure TForm1.edtTrIdChange(Sender: TObject);
begin
  // TR_ID가 변경되면 URL도 자동 업데이트
  if not sgcWebSocketClient1.Active then
    UpdateWebSocketURL;
end;

procedure TForm1.LogMessage(const Msg: string);
begin
  Memo1.Lines.Add(FormatDateTime('[hh:nn:ss] ', Now) + Msg);
  if Memo1.Lines.Count > 0 then
    Memo1.Perform(EM_SCROLLCARET, 0, 0);
end;

procedure TForm1.btnConnectClick(Sender: TObject);
var
  trId: string;
begin
  APPROVAL_KEY := Trim(edtApprovalKey.Text);
  trId := Trim(edtTrId.Text);
  
  if APPROVAL_KEY = '' then
  begin
    ShowMessage('Approval Key를 입력해주세요.');
    edtApprovalKey.SetFocus;
    Exit;
  end;
  
  if trId = '' then
  begin
    ShowMessage('TR_ID를 입력해주세요.');
    edtTrId.SetFocus;
    Exit;
  end;
  
  try
    // URL 최종 확인 및 업데이트
    UpdateWebSocketURL;
    
    LogMessage('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    LogMessage('웹소켓 연결 시도...');
    LogMessage('TR_ID: ' + trId);
    sgcWebSocketClient1.Active := True;
  except
    on E: Exception do
    begin
      LogMessage('연결 실패: ' + E.Message);
      ShowMessage('연결 실패: ' + E.Message);
    end;
  end;
end;

procedure TForm1.btnDisconnectClick(Sender: TObject);
begin
  if sgcWebSocketClient1.Active then
  begin
    LogMessage('연결 해제 중...');
    sgcWebSocketClient1.Active := False;
  end;
end;

procedure TForm1.SendSubscription(const TrType: string);
var
  jHeader, jBody, jInput, jSend: TJSONObject;
  sJson: string;
begin
  if not sgcWebSocketClient1.Active then
  begin
    ShowMessage('웹소켓이 연결되지 않았습니다.');
    Exit;
  end;

  jHeader := TJSONObject.Create;
  jInput := TJSONObject.Create;
  jBody := TJSONObject.Create;
  jSend := TJSONObject.Create;

  try
    // Header 구성
    jHeader.AddPair('approval_key', APPROVAL_KEY);
    jHeader.AddPair('custtype', 'P');
    jHeader.AddPair('tr_type', TrType);
    jHeader.AddPair('content-type', 'utf-8');

    // Input 구성
    jInput.AddPair('tr_id', 'H0STCNT0');
    jInput.AddPair('tr_key', '000660');

    // Body 구성
    jBody.AddPair('input', jInput);  // jInput 소유권은 jBody가 가져감

    // 전체 JSON 구성
    jSend.AddPair('header', jHeader); // jHeader 소유권은 jSend가 가져감
    jSend.AddPair('body', jBody);     // jBody 소유권은 jSend가 가져감

    sJson := jSend.ToJSON;

    LogMessage('전송 데이터: ' + sJson);
    sgcWebSocketClient1.WriteData(sJson);

    if TrType = '1' then
      LogMessage('구독 요청 전송 완료')
    else
      LogMessage('구독 해제 요청 전송 완료');

  finally
    // ✅ 하위 객체는 해제하지 말고, 최상위 객체(jSend)만 해제
    jSend.Free;
  end;
end;

procedure TForm1.btnSubscribeClick(Sender: TObject);
begin
  SendSubscription('1');
end;

procedure TForm1.btnUnsubscribeClick(Sender: TObject);
begin
  SendSubscription('2');
end;

procedure TForm1.sgcWebSocketClient1Connect(Connection: TsgcWSConnection);
begin
  LogMessage('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  LogMessage('✓ 웹소켓 연결 성공!');
  LogMessage('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  
  btnConnect.Enabled := False;
  btnSubscribe.Enabled := True;
  btnUnsubscribe.Enabled := True;
  btnDisconnect.Enabled := True;
  edtApprovalKey.Enabled := False;

end;

procedure TForm1.sgcWebSocketClient1Disconnect(Connection: TsgcWSConnection; Code: Integer);
begin
  LogMessage('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  LogMessage('✗ 웹소켓 연결 해제됨');
  LogMessage('종료 코드: ' + IntToStr(Code));
  LogMessage('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  
  btnConnect.Enabled := True;
  btnSubscribe.Enabled := False;
  btnUnsubscribe.Enabled := False;
  btnDisconnect.Enabled := False;
  edtApprovalKey.Enabled := True;

end;

procedure TForm1.sgcWebSocketClient1Message(Connection: TsgcWSConnection; const Text: string);
var
  jResponse: TJSONObject;
  jHeader, jBody: TJSONObject;
  trId, rtCd, msgCd, msg1: string;
begin
  LogMessage('수신: ' + Text);
  
  try
    jResponse := TJSONObject.ParseJSONValue(Text) as TJSONObject;
    if Assigned(jResponse) then
    try
      // Header 파싱
      if jResponse.TryGetValue<TJSONObject>('header', jHeader) then
      begin
        jHeader.TryGetValue<string>('tr_id', trId);
        LogMessage('TR_ID: ' + trId);
      end;
      
      // Body 파싱
      if jResponse.TryGetValue<TJSONObject>('body', jBody) then
      begin
        // 응답 코드 확인
        rtCd := jBody.GetValue<string>('rt_cd', '');
        msgCd := jBody.GetValue<string>('msg_cd', '');
        msg1 := jBody.GetValue<string>('msg1', '');
        
        if rtCd <> '' then
        begin
          if rtCd = '0' then
            LogMessage('✓ 성공: ' + msg1 + ' [' + msgCd + ']')
          else
            LogMessage('✗ 실패: ' + msg1 + ' [' + msgCd + ']');
        end
        else
        begin
          // 실시간 체결 데이터
          LogMessage('실시간 데이터: ' + jBody.ToJSON);
        end;
      end;
      
    finally
      jResponse.Free;
    end;
  except
    on E: Exception do
      LogMessage('메시지 파싱 오류: ' + E.Message);
  end;
end;

procedure TForm1.sgcWebSocketClient1Error(Connection: TsgcWSConnection; const Error: string);
begin
  LogMessage('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  LogMessage('❌ 에러 발생: ' + Error);
  LogMessage('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  ShowMessage('에러: ' + Error);
end;

end.