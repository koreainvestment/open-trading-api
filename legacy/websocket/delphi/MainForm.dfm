object Form1: TForm1
  Left = 0
  Top = 0
  Caption = #54620#44397#53804#51088#51613#44428' WebSocket '#53580#49828#53944' v1.0'
  ClientHeight = 600
  ClientWidth = 750
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -12
  Font.Name = 'Segoe UI'
  Font.Style = []
  Position = poScreenCenter
  OnCreate = FormCreate
  TextHeight = 15
  object Label1: TLabel
    Left = 24
    Top = 24
    Width = 73
    Height = 15
    Caption = 'Approval Key:'
  end
  object Label2: TLabel
    Left = 24
    Top = 58
    Width = 32
    Height = 15
    Caption = 'TR_ID:'
  end
  object Label3: TLabel
    Left = 24
    Top = 92
    Width = 89
    Height = 15
    Caption = 'TR_KEY:'#51333#47785#53076#46300
  end
  object edtApprovalKey: TEdit
    Left = 120
    Top = 21
    Width = 420
    Height = 23
    TabOrder = 0
    TextHint = 'Approval Key '#51077#47141' (e.g. e44ffe64-7a22-...)'
  end
  object edtTrId: TEdit
    Left = 120
    Top = 55
    Width = 150
    Height = 23
    TabOrder = 1
    Text = 'H0STCNT0'
    TextHint = 'TR_ID ('#50696': H0STCNT0)'
    OnChange = edtTrIdChange
  end
  object edtTrKey: TEdit
    Left = 120
    Top = 89
    Width = 150
    Height = 23
    TabOrder = 2
    Text = '005930'
    TextHint = #51333#47785#53076#46300' ('#50696': 005930)'
  end
  object btnConnect: TButton
    Left = 560
    Top = 19
    Width = 170
    Height = 30
    Caption = #50672#44208
    TabOrder = 3
    OnClick = btnConnectClick
  end
  object btnSubscribe: TButton
    Left = 560
    Top = 55
    Width = 80
    Height = 30
    Caption = #44396#46021
    TabOrder = 4
    OnClick = btnSubscribeClick
  end
  object btnUnsubscribe: TButton
    Left = 650
    Top = 55
    Width = 80
    Height = 30
    Caption = #44396#46021#54644#51228
    TabOrder = 5
    OnClick = btnUnsubscribeClick
  end
  object btnDisconnect: TButton
    Left = 560
    Top = 91
    Width = 170
    Height = 30
    Caption = #50672#44208' '#54644#51228
    TabOrder = 6
    OnClick = btnDisconnectClick
  end
  object Memo1: TMemo
    Left = 24
    Top = 136
    Width = 706
    Height = 441
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWindowText
    Font.Height = -12
    Font.Name = 'Consolas'
    Font.Style = []
    ParentFont = False
    ScrollBars = ssVertical
    TabOrder = 7
  end
  object sgcWebSocketClient1: TsgcWebSocketClient
    Port = 80
    ConnectTimeout = 0
    ReadTimeout = -1
    WriteTimeout = 0
    TLS = False
    Proxy.Enabled = False
    Proxy.Port = 8080
    Proxy.ProxyType = pxyHTTP
    HeartBeat.Enabled = True
    HeartBeat.HeartBeatType = hbtAlways
    HeartBeat.Interval = 30000
    HeartBeat.Timeout = 0
    IPVersion = Id_IPv4
    OnConnect = sgcWebSocketClient1Connect
    OnMessage = sgcWebSocketClient1Message
    OnDisconnect = sgcWebSocketClient1Disconnect
    OnError = sgcWebSocketClient1Error
    Authentication.Enabled = False
    Authentication.URL.Enabled = True
    Authentication.Session.Enabled = False
    Authentication.Basic.Enabled = False
    Authentication.Token.Enabled = False
    Authentication.Token.AuthName = 'Bearer'
    Extensions.DeflateFrame.Enabled = False
    Extensions.DeflateFrame.WindowBits = 15
    Extensions.PerMessage_Deflate.Enabled = False
    Extensions.PerMessage_Deflate.ClientMaxWindowBits = 15
    Extensions.PerMessage_Deflate.ClientNoContextTakeOver = False
    Extensions.PerMessage_Deflate.MemLevel = 9
    Extensions.PerMessage_Deflate.ServerMaxWindowBits = 15
    Extensions.PerMessage_Deflate.ServerNoContextTakeOver = False
    Options.CleanDisconnect = False
    Options.FragmentedMessages = frgOnlyBuffer
    Options.Parameters = '/'
    Options.RaiseDisconnectExceptions = True
    Options.ValidateUTF8 = False
    Specifications.Drafts.Hixie76 = False
    Specifications.RFC6455 = True
    NotifyEvents = neAsynchronous
    LogFile.Enabled = False
    QueueOptions.Binary.Level = qmNone
    QueueOptions.Ping.Level = qmNone
    QueueOptions.Text.Level = qmNone
    WatchDog.Attempts = 0
    WatchDog.Enabled = False
    WatchDog.Interval = 10
    Throttle.BitsPerSec = 0
    Throttle.Enabled = False
    LoadBalancer.Enabled = False
    LoadBalancer.Port = 0
    LoadBalancer.TLS = False
    TLSOptions.VerifyCertificate = False
    TLSOptions.VerifyDepth = 0
    TLSOptions.Version = tlsUndefined
    TLSOptions.IOHandler = iohOpenSSL
    TLSOptions.OpenSSL_Options.APIVersion = oslAPI_1_0
    TLSOptions.OpenSSL_Options.LegacyProvider.Enabled = False
    TLSOptions.OpenSSL_Options.LegacyProvider.LibPath = oslpNone
    TLSOptions.OpenSSL_Options.LibPath = oslpNone
    TLSOptions.OpenSSL_Options.UnixSymLinks = oslsSymLinksDefault
    TLSOptions.OpenSSL_Options.VersionMin = tlsUndefined
    TLSOptions.OpenSSL_Options.X509Checks.Mode = []
    TLSOptions.SChannel_Options.CertStoreName = scsnMY
    TLSOptions.SChannel_Options.CertStorePath = scspStoreCurrentUser
    TLSOptions.SChannel_Options.UseLegacyCredentials = False
    Left = 400
    Top = 64
  end
end
