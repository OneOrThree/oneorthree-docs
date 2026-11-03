"""v6: 흐름별 정렬과 상세 컴포넌트 설명으로 SVG/XML/HTML을 함께 생성한다.

v6은 /screens BFF·Realtime 사건 입구·outbox REALTIME 대상·위성 배치를 반영한다(phone main c247e71).

운영 실측을 주장하지 않는다. main 대조 커밋과 배포 미확인 상태를 도면에 남긴다.
archify v3 HTML은 최초 실행 시 보존하며 다른 도면은 수정하지 않는다.
"""
import importlib
import json
from html import escape
from shutil import copy2

base = importlib.import_module("make-architecture-diagrams")
ROOT = base.ROOT
VERSION = 6
base.TARGET_VERSIONS.update({"03-service": VERSION, "04-system": VERSION})
COMMIT = "c247e7108b1296a3f76c280553fa8779d221d753"


def frame(name, title, height):
    d = base.Diagram(name, title,
                     "2026.09.19 · phone main c247e71 · 역할·정본·전달·운영 상태 · main 구현과 운영 활성화는 별도", height)
    d.band(40, 120, 1680, 70, "상태")
    d.legend_items = [(180,155,"main 구현 · 운영 별도",""),
                      (680,155,"구현 · 기본 OFF · 수동 적용","8 5"),
                      (1180,155,"설계 · 배포 미확정","2 5")]
    return d


def text_width(value, size):
    return sum(size if ord(ch) > 127 and ch not in "·→" else size * 0.56 for ch in value)


def box(d, ident, x, y, w, h, title, lines, kind="core", stage="", state="code"):
    """v5와 같은 상자 문법. 줄 수·글자 폭이 상자를 넘으면 생성을 멈춘다."""
    assert 59 + (len(lines)-1)*24 < h-30, ident
    assert text_width(title, 21) <= w-30, (ident, title)
    for line in lines + [stage]:
        assert text_width(line, 16) <= w-30, (ident, line)
    d.box(ident, x, y, w, h, title, lines, kind, stage, state)


def service():
    d = frame("03-service", "Gromo · 서비스 아키텍처", 2090)
    b = lambda *a, **k: box(d, *a, **k)
    d.band(40, 210, 1680, 520, "공개 REST · /screens BFF", "공개 계약은 Business, 코어 정본은 Data가 소유한다.")
    b("app", 60, 300, 260, 120, "모바일 앱", ["REST 명령 · 화면 조회", "React Native · Expo"], stage="클라이언트")
    b("business", 440, 300, 360, 270, "Business API",
      ["공개 인증 · 응답 봉투 · 서비스 토큰", "/screens 14종 · 조각 병렬 조합",
       "launch · raft · account · explore", "visit · home · focus · town-hall",
       "board · library · shop · playback", "mailbox · friends",
       "빈 조각은 missingFragments"], stage="main 구현 · 영속 DB 없음")
    b("data", 920, 300, 360, 270, "Data API",
      ["/internal/* · 레거시 /api/v1", "권한 · 정산 · 원장 · receipt",
       "9/19 추가: 가입·초대 · 외양", "공지 · 퀘스트 · 방송기 · 섬 관리",
       "계정 조회·수정 · 탈퇴 파기", "상점은 테이블 선구축만"], stage="main 구현 · 코어 정본 소유")
    b("coreDb", 1400, 300, 300, 150, "코어 DB", ["gromo · PostgreSQL", "상태 · 원장 · receipt · outbox", "링크 원장도 코어 DB(A23)"],
      "data", "Data 전용")
    b("previewRedis", 60, 600, 260, 120, "미리보기 Redis", ["Business 전용 · 128mb", "allkeys-lru · 비영속"], "data", "main · 재생성 가능")
    b("notiApi", 920, 600, 360, 120, "Notification · 설정", ["기기 토큰 · 알림 설정 · 결과 ack", "Business만 HTTP로 호출"], "event", "main 구현 · 위성 수동 기동")
    d.edge("appRest", "app", "business", [(320,355),(440,355)], "REST", (380,345), state="code")
    d.edge("internalHttp", "business", "data", [(800,355),(920,355)], "/internal", (860,345), state="code")
    d.edge("coreWrite", "data", "coreDb", [(1280,355),(1400,355)], "단일 TX", (1340,345), state="code")
    d.edge("previewCache", "business", "previewRedis", [(480,570),(480,655),(320,655)], "TTL 캐시", (400,645), state="code")
    d.edge("notiSettings", "business", "notiApi", [(800,530),(860,530),(860,655),(920,655)], "기기·설정", (860,600), state="code")

    d.band(40, 760, 1680, 470, "실시간 · 편지 · 사건 수신", "Realtime은 사건을 두 입구로 받는다.")
    b("socketApp", 60, 850, 260, 120, "모바일 앱", ["STOMP 구독 · 편지", "CONNECT Bearer 인증"], stage="클라이언트")
    b("realtime", 440, 850, 360, 200, "Realtime",
      ["/ws/chat · /ws/realtime STOMP", "편지 저장 · 조회 · fanout", "사건 입구 POST /internal/events",
       "Kafka realtime-events 입구(선택)", "앱 사건 14종은 수신만 · 구독 닫힘"], "event", "main 구현 · dev overlay")
    b("chatRedis", 920, 850, 360, 170, "채팅·집중 Redis",
      ["chat:fanout Pub/Sub · 재생 불가", "presence:focus:* 순번 조건부", "탈퇴 tombstone · 끝난 세션 표식",
       "Data 쓰기 · Realtime 읽기"], "data", "main dev · ACL 미적용")
    b("chatDb", 60, 1070, 260, 150, "편지 DB", ["gromo_chat · 편지 정본", "inbound_events", "eventId PK · 중복 거름"], "data", "Realtime 소유 · dev")
    d.edge("mailboxHttp", "business", "realtime", [(700,570),(700,850)], "우체통 HTTP", (700,745), state="code")
    d.edge("appSocket", "socketApp", "realtime", [(320,905),(440,905)], "STOMP", (380,895), state="code")
    d.edge("chatFanout", "realtime", "chatRedis", [(800,905),(920,905)], "읽기 · fanout", (860,895), state="code")
    d.edge("focusPresence", "data", "chatRedis", [(1280,530),(1340,530),(1340,960),(1280,960)], "presence 쓰기", (1340,800), state="code")
    d.edge("chatPersistence", "realtime", "chatDb", [(480,1050),(480,1140),(320,1140)], "저장 · 수신 기록", (400,1130), state="code")

    d.band(40, 1260, 1680, 460, "outbox 전달 · 알림 · relay 기본 OFF", "상태·receipt·outbox는 같은 TX.")
    b("outboxSource", 60, 1350, 260, 170, "Data · outbox",
      ["상태 · receipt · outbox", "같은 TX로 사건 보존", "대상 4종: KAFKA · NOTI", "LINK · REALTIME"], stage="코어 DB 소유")
    b("relay", 440, 1350, 360, 180, "Outbox relay",
      ["Data 안 · lease · 대상별 재시도", "대상마다 경로 하나", "REALTIME: HTTP 기본 · Kafka 선택",
       "OUTBOX_RELAY_ENABLED=false"], "event", "main 구현 · 기본 OFF", "off")
    b("kafka", 920, 1350, 360, 150, "Kafka",
      ["notification-events · userId 키", "realtime-events · 플래그 선택", "KRaft 1노드 · RF 1 · DLT"],
      "event", "dev overlay · 활성화 미확인", "off")
    b("notification", 1400, 1350, 300, 190, "Notification",
      ["입구: Kafka 소비 · HTTP", "POST /internal/events", "eventId 중복 제거 · version", "템플릿 · 이력 · FCM 발송"],
      "event", "소비·스케줄 기본 OFF", "off")
    b("link", 440, 1580, 360, 120, "링크 서버", ["레포 밖 · Vercel origin", "A23 흡수 결정 · LINK 대상 잔존"],
      "external", "외부 · 흡수 예정", "unknown")
    b("notiDb", 1400, 1580, 300, 120, "알림 DB", ["gromo_notification", "Notification 소유"], "data", "prod RDS 별도 DB: 목표", "off")
    d.edge("relayOwnership", "outboxSource", "relay", [(320,1405),(440,1405)], "outbox", (380,1395), state="off")
    d.edge("relayKafka", "relay", "kafka", [(800,1405),(920,1405)], "KAFKA", (860,1395), state="off")
    d.edge("kafkaConsume", "kafka", "notification", [(1280,1405),(1400,1405)], "소비", (1340,1395), state="off")
    d.edge("relayNoti", "relay", "notification", [(800,1520),(1400,1520)], "NOTI · HTTP", (1100,1520), state="off")
    d.edge("relayRealtime", "relay", "realtime", [(700,1350),(700,1050)], "REALTIME · HTTP 기본", (700,1245), state="off")
    d.edge("kafkaRealtime", "kafka", "realtime", [(1000,1350),(1000,1035),(800,1035)], "realtime-events", (1000,1245), state="off")
    d.edge("relayLink", "relay", "link", [(620,1530),(620,1580)], "LINK · HTTP", (690,1560), state="off")
    d.edge("notificationWrite", "notification", "notiDb", [(1550,1540),(1550,1580)], "저장", (1600,1563), state="off")

    d.band(40, 1750, 1680, 215, "랭킹 · Target-2 · 조건 충족 후 도입")
    b("score", 60, 1815, 330, 120, "score-events · DLT", ["Data outbox · 절대 점수 + version"], "future", "설계 · 알림과 별도 스트림", "plan")
    b("rankConsumer", 600, 1815, 330, 120, "랭킹 컨슈머", ["중복 · 역순 적용 수렴"], "future", "설계 · 조건 충족 후 도입", "plan")
    b("rankRedis", 1130, 1815, 570, 120, "랭킹 Redis", ["완료 ZSET + 라이브 presence · 정본 DB에서 재구축"], "future", "설계 · 코어 정본의 projection", "plan")
    d.edge("scoreConsume", "score", "rankConsumer", [(390,1875),(600,1875)], "소비", (495,1865), state="plan")
    d.edge("rankProject", "rankConsumer", "rankRedis", [(930,1875),(1130,1875)], "반영", (1030,1865), state="plan")
    d.band(40, 1995, 1680, 55, "흐름별로 같은 서비스를 다시 표시했다. 상점 상품·지갑과 통계 조각은 아직 missingFragments다.")
    return d


def system():
    d = frame("04-system", "Gromo · 시스템 아키텍처", 1780)
    b = lambda *a, **k: box(d, *a, **k)
    d.band(40, 210, 1680, 410, "prod · AWS gromo-prod", "컨테이너는 app · nginx · datadog-agent, DB는 RDS다.")
    b("app", 60, 300, 240, 130, "모바일 앱", ["HTTPS · 공개 REST", "React Native · Expo"], stage="클라이언트")
    b("cloudflare", 380, 300, 260, 130, "Cloudflare", ["DNS · 프록시", "Origin 인증서"], "external", "prod 공개 진입")
    b("nginx", 700, 300, 340, 170, "nginx :443",
      ["TLS 종료 · /api/v1 → Data", "위성 include: 무접두 → Business", "/internal/admin → Notification",
       "그 밖의 /internal · /actuator 404"], stage="prod · include 수동 적용")
    b("dataProd", 1100, 300, 280, 130, "Data API · prod", ["app 컨테이너 · /api/v1", "코어 정본 gromo 접근"], stage="release → ECR · SSM")
    b("prodRds", 1440, 300, 260, 130, "RDS PostgreSQL", ["gromo-prod-db · 코어", "gromo_notification: 목표"], "data", "prod · 알림 DB 미확인")
    b("prodCd", 60, 470, 400, 120, "prod 배포", ["release push → ECR 이미지", "compose → S3 → SSM send-command"], "external", "prod-cd.yml")
    b("datadog", 1100, 480, 190, 110, "datadog-agent", ["APM · 로그"], "external", "prod 사이드카")
    b("s3", 1310, 480, 200, 120, "S3 로그 버킷", ["gromo-prod-logs", "접두 3개 · 90일 만료"], "data", "적용 2026-09-19")
    for ident, src, dst, points, label, at in [
        ("appCf", "app", "cloudflare", [(300,365),(380,365)], "HTTPS", (340,355)),
        ("cfNginx", "cloudflare", "nginx", [(640,365),(700,365)], "Proxy", (670,355)),
        ("nginxData", "nginx", "dataProd", [(1040,365),(1100,365)], "/api/v1", (1070,355)),
        ("dataRds", "dataProd", "prodRds", [(1380,365),(1440,365)], "JDBC", (1410,355)),
        ("dataDatadog", "dataProd", "datadog", [(1180,430),(1180,480)], "APM", (1225,460)),
        ("dataLogs", "dataProd", "s3", [(1350,430),(1350,480)], "app.log", (1405,460))]:
        d.edge(ident, src, dst, points, label, at, state="code")

    d.band(40, 650, 1680, 270, "위성 · satellites.yml 수동 적용", "prod·dev 호스트 공통 · CD 없음")
    b("business", 600, 740, 320, 150, "Business API · :8080",
      ["공개 인증 · /screens 14종", "내부 호출: Data · Notification", "Realtime 우체통 · 영속 DB 없음"], stage="satellites.yml · 수동")
    b("notification", 980, 740, 320, 150, "Notification · :8082",
      ["/internal/admin 콘솔", "Kafka 소비 · HTTP 사건 입구", "FCM 발송 · 전용 DB"], "event", "소비·스케줄 기본 OFF", "off")
    b("previewRedis", 260, 740, 280, 150, "미리보기 Redis", ["business-redis · 128mb", "allkeys-lru · 비영속"], "data", "Business 전용")
    d.edge("nginxBusiness", "nginx", "business", [(780,470),(780,740)], "무접두 · /screens", (780,635), state="off")
    d.edge("nginxNotification", "nginx", "notification", [(1010,470),(1010,740)], "/internal/admin", (1010,635), state="off")
    d.edge("businessPreview", "business", "previewRedis", [(600,815),(540,815)], "캐시", (570,805), state="code")
    d.edge("notificationDb", "notification", "prodRds", [(1300,800),(1600,800),(1600,430)], "gromo_notification", (1600,635), state="off")

    d.band(40, 950, 1680, 580, "dev · GCP gromo-dev-app", "main push → GAR 자동 배포 · 오버레이는 있을 때만 겹친다")
    b("realtime", 60, 1040, 420, 150, "Realtime · :8081",
      ["/ws/chat · /ws/realtime STOMP", "POST /internal/events 사건 입구", "편지 · inbound_events 저장"], "event", "dev overlay 전용 · prod 없음")
    b("devData", 600, 1040, 320, 150, "Data API · :8080", ["dev app · 코어 정본", "presence 조건부 쓰기", "relay 내장 · 기본 OFF"], stage="main push → GAR 자동")
    b("kafka", 980, 1040, 320, 150, "Kafka overlay",
      ["내부 :9092 · KRaft 1노드", "notification-events", "realtime-events (선택)"], "event", "dev overlay · 수동", "off")
    b("chatRedis", 300, 1240, 460, 120, "Redis · 채팅·집중", ["chat:fanout · presence:focus:*", "탈퇴 tombstone"], "data", "dev compose · ACL 미적용")
    b("devPg", 60, 1400, 860, 100, "PostgreSQL 컨테이너", ["gromo: Data / gromo_chat: Realtime · 같은 인스턴스 별도 database"], "data", "dev compose")
    b("devCd", 1360, 1040, 340, 150, "dev 배포", ["main push → GAR back:<sha>", "self-hosted 러너 → VM", "gromo/dev/env · 오버레이"], "external", "dev-cd.yml")
    d.edge("businessData", "business", "devData", [(760,890),(760,1040)], "/internal", (760,935), state="code")
    d.edge("kafkaNotification", "kafka", "notification", [(1130,1040),(1130,890)], "소비", (1130,935), state="off")
    d.edge("dataKafka", "devData", "kafka", [(920,1100),(980,1100)], "relay", (950,1090), state="off")
    d.edge("dataRealtime", "devData", "realtime", [(600,1100),(480,1100)], "REALTIME", (540,1090), state="off")
    d.edge("realtimeRedis", "realtime", "chatRedis", [(400,1190),(400,1240)], "fanout", (440,1220), state="code")
    d.edge("dataRedis", "devData", "chatRedis", [(650,1190),(650,1240)], "presence", (705,1220), state="code")
    d.edge("realtimeDb", "realtime", "devPg", [(150,1190),(150,1400)], "gromo_chat", (150,1300), state="code")
    d.edge("devDataDb", "devData", "devPg", [(850,1190),(850,1400)], "gromo", (850,1300), state="code")

    b("rankRedis", 60, 1560, 660, 150, "Target-2 · 랭킹 Redis",
      ["score-events · 알림과 별도 스트림 · 소비자", "리그 p95 > 1.5초 / findRankOf p95 > 500ms", "또는 Business 다중 인스턴스 필요"],
      "future", "설계 · 조건 충족 후 도입", "plan")
    b("wssPolicy", 760, 1560, 940, 150, "prod WSS · 배포 미확정",
      ["prod compose에 Realtime·Kafka·Redis가 아직 없다", "TLS 종료 · rate limit · 연결 수 상한을 배포 전에 확정",
       "편지 DB prod 배치 · Redis ACL 적용 후속 확인"], "future", "prod 배포 미확정", "unknown")
    return d


def write_html(d):
    """동일 SVG·노드·간선으로 연결 강조와 문서 보기·다운로드를 제공한다."""
    diagram_dir = ROOT / "diagrams"
    current = diagram_dir / f"{d.name}.html"
    previous = diagram_dir / f"{d.name}.v{VERSION-1}.html"
    if current.exists() and not previous.exists():
        archived = current.read_text()
        for suffix in ('svg', 'drawio.xml'):
            archived = archived.replace(f'href="{d.name}.{suffix}"',
                                        f'href="{d.name}.v{VERSION-1}.{suffix}"')
        previous.write_text(archived)
    source = diagram_dir / f'{d.name}.source.json'
    source_version = json.loads(source.read_text())['version'] if source.exists() else None
    # 버전 근거가 있는 동반 산출물만 보존한다. R61 HTML과 오래된 SVG의 판은 다르다.
    for suffix in ('svg', 'drawio.xml', 'source.json'):
        legacy = diagram_dir / f'{d.name}.{suffix}'
        archive = diagram_dir / f'{d.name}.v{source_version}.{suffix}'
        if source_version is not None and source_version < VERSION and legacy.exists() and not archive.exists():
            copy2(legacy, archive)
    d.write(archive=False)
    svg = (diagram_dir / f"{d.name}.svg").read_text()
    graph = {"nodes":d.nodes,"edges":d.edges}
    graph_json = json.dumps(graph, ensure_ascii=False).replace("<", "\\u003c")
    rows = []
    for n in d.nodes:
        outgoing = [f'{e["label"] or "연결"} → {next(x["title"] for x in d.nodes if x["id"] == e["target"])}' for e in d.edges if e["source"] == n["id"]]
        incoming = [f'{next(x["title"] for x in d.nodes if x["id"] == e["source"])} → {e["label"] or "연결"}' for e in d.edges if e["target"] == n["id"]]
        rows.append(f'<article><h2>{escape(n["title"])}</h2><p>{escape(" · ".join(n["lines"]))}</p><p>{escape(n["stage"])}</p><ul>' + "".join(f"<li>{escape(v)}</li>" for v in incoming+outgoing) + '</ul></article>')
    template = '''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title><style>
*{box-sizing:border-box}body{margin:0;color:#172b3a;background:#fff;font-family:"Apple SD Gothic Neo","Noto Sans KR",sans-serif}
header{position:sticky;top:0;z-index:2;background:#fff;border-bottom:1px solid #dce4eb;padding:12px 16px;display:flex;gap:8px;flex-wrap:wrap;align-items:center}
button,a{font:inherit;font-size:13px;border:1px solid #dce4eb;border-radius:6px;padding:7px 10px;background:#f8fafc;color:#172b3a;text-decoration:none;cursor:pointer}
button[aria-pressed=true]{background:#edf4fc;border-color:#3866a0}#hint{margin:0;font-size:12px;color:#4d5a66;flex-basis:100%}
#viewport{overflow:auto;height:calc(100vh - 105px);min-height:400px}svg{display:block;width:100%;height:auto;min-width:900px}
[data-cell-id]{transition:opacity .15s}g[role=button]{cursor:pointer}g[role=button]:focus{outline:none}g[role=button]:focus rect{stroke:#172b3a;stroke-width:4}
.dim{opacity:.16}#text{max-width:1000px;margin:0 auto;padding:20px}article{border-bottom:1px solid #dce4eb;padding:12px 0}h2{font-size:20px}li,p{line-height:1.7}
[hidden]{display:none!important}@media print{header{position:static}header button{display:none}#viewport{height:auto;overflow:visible}svg{width:100%!important;min-width:0}}
</style></head><body><header>
<button id="diagram" aria-pressed="true">다이어그램</button><button id="textView" aria-pressed="false">문서 보기</button>
<button id="fit">전체 보기</button><button id="zoomIn" aria-label="확대">＋</button><button id="zoomOut" aria-label="축소">−</button><button id="reset">연결 강조 해제</button>
<a href="__NAME__.svg" download>SVG ↓</a><a href="__NAME__.drawio.xml" download>draw.io 원본 ↓</a>
<a href="/spec/__DETAIL__" target="_top">근거 문서</a><p id="hint" aria-live="polite">상자를 선택하면 연결을 강조합니다. Esc로 해제 · 실선은 main 구현이며 운영 실측을 뜻하지 않습니다.</p>
</header><main><div id="viewport">__SVG__</div><section id="text" hidden>__ROWS__</section></main>
<script type="application/json" id="graph">__GRAPH__</script><script>
const graph=JSON.parse(document.getElementById('graph').textContent),svg=document.querySelector('svg'),hint=document.getElementById('hint');let zoom=1;
function reset(){svg.querySelectorAll('[data-cell-id]').forEach(el=>el.classList.remove('dim'));hint.textContent='상자를 선택하면 연결을 강조합니다. Esc로 해제 · 실선은 main 구현이며 운영 실측을 뜻하지 않습니다.';}
function select(id){const ids=new Set([id]);graph.edges.filter(e=>e.source===id||e.target===id).forEach(e=>{ids.add(e.id);ids.add(e.source);ids.add(e.target)});svg.querySelectorAll('[data-cell-id]').forEach(el=>el.classList.toggle('dim',!ids.has(el.dataset.cellId)));const n=graph.nodes.find(n=>n.id===id);hint.textContent=n.title+' · '+n.lines.join(' · ')+' · '+n.stage;}
graph.nodes.forEach(n=>{const el=svg.querySelector('[data-cell-id="'+n.id+'"]');el.setAttribute('role','button');el.setAttribute('tabindex','0');el.setAttribute('aria-label',n.title+' '+n.stage);el.addEventListener('click',()=>select(n.id));el.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();select(n.id)}})});
document.getElementById('reset').onclick=reset;document.addEventListener('keydown',e=>{if(e.key==='Escape')reset()});
function scale(v){zoom=Math.max(.5,Math.min(3,v));svg.style.width=(zoom*100)+'%';svg.style.minWidth=zoom===1?'0':'900px';}
document.getElementById('fit').onclick=()=>scale(1);document.getElementById('zoomIn').onclick=()=>scale(zoom+.25);document.getElementById('zoomOut').onclick=()=>scale(zoom-.25);
function view(text){document.getElementById('text').hidden=!text;document.getElementById('viewport').hidden=text;document.getElementById('diagram').setAttribute('aria-pressed',String(!text));document.getElementById('textView').setAttribute('aria-pressed',String(text));}
document.getElementById('diagram').onclick=()=>view(false);document.getElementById('textView').onclick=()=>view(true);
</script></body></html>'''
    detail = {'01-ia': 'use-cases', '02-journey': 'use-cases', '03-service': 'service-architecture', '04-system': 'system-architecture'}[d.name]
    html = template.replace('__TITLE__',escape(d.title)).replace('__NAME__',d.name).replace('__DETAIL__', detail).replace('__SVG__',svg).replace('__ROWS__',''.join(rows)).replace('__GRAPH__',graph_json)
    current.write_text(html)
    (diagram_dir / f"{d.name}.source.json").write_text(json.dumps({"version":VERSION,"sourceCommit":COMMIT,"title":d.title,**graph},ensure_ascii=False,indent=2)+"\n")


if __name__ == '__main__':
    manifest = json.loads((ROOT / 'diagrams' / 'manifest.json').read_text())
    for name in ('03-service','04-system'):
        entry=next(e for e in manifest if e['id']==name)
        if entry['versions'][0]['id'] != f'v{VERSION}':
            raise SystemExit(f'{name}: manifest의 현재 버전을 v{VERSION}로 등록한 뒤 생성하세요.')
    for d in (service(),system()):
        write_html(d)
