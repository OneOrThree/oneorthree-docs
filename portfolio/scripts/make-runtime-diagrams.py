"""2026-11-18 phone main과 고정한 cattus-infra revision으로 운영 연결과 로그 경로를 그린다."""
import importlib

reviewed = importlib.import_module('make-reviewed-architecture-diagrams')
base = reviewed.base
INFRA_COMMIT = '69edca4d5f9ef920a29cdba7f78dcca35e1be112'


def frame(name, title, height):
    d = base.Diagram(name, title,
                     '2026.11.18 · phone 1281cbfc4 + infra 69edca4d(11-04 고정) · 배포 설정 대조 + 11/03 S3·앱 호스트 확인 · 검증 범위는 근거 문서', height)
    d.infra_source_commit = INFRA_COMMIT
    return d


def box(d, ident, x, y, title, lines, stage, kind='core', state='code', h=190):
    reviewed.box(d, ident, x, y, 450, h, title, lines, kind, stage, state)


def edge(d, ident, source, target, points, label='', at=None, state='code'):
    d.edge(ident, source, target, points, label, at, state=state)


def system():
    d = frame('04-system', 'Cattus · 운영 호스트·컨테이너·포트', 3460)
    d.band(40, 140, 1680, 290, '01 · 공개 진입', 'Cloudflare 프록시 → Origin TLS. app·backoffice의 80/443은 Cloudflare IPv4만 허용한다.')
    box(d, 'client', 70, 225, '모바일 앱', ['HTTPS REST · WSS', 'catus-api-v2.oneorthree.world', '단체 채팅: REST + 10초 폴링'], 'React Native · Expo', 'external')
    box(d, 'cf', 655, 225, 'Cloudflare', ['DNS · 프록시', 'Origin 인증서로 nginx에 HTTPS', 'ALB 없이 EC2 nginx로 진입'], '앱 / 백오피스 호스트 별도', 'external')
    box(d, 'nginx', 1240, 225, 'nginx · 앱 호스트', ['호스트 :80 → HTTPS / :443 TLS', '공개 allowlist → Business · reports 미허용', '/ws/realtime → Realtime', '/internal · /actuator → 404'], 'nginx:1.28-alpine · 로그 stdout/stderr')
    edge(d, 'internet', 'client', 'cf', [(520,310),(655,310)], '443', (588,300))
    edge(d, 'origin', 'cf', 'nginx', [(1105,310),(1240,310)], '443', (1172,300))

    d.band(40, 480, 1680, 620, '02 · catus-prod-V2 · m6g.large · Docker app-network',
           'nginx와 아래 서버 4종이 한 EC2를 공유한다. 서버 포트는 브리지 내부, 관리 프록시만 사설 IP에 bind한다.')
    box(d, 'business', 70, 580, 'Business · :8080', ['공개 인증·응답·/screens 조합', 'Data·Realtime·Notification 내부 HTTP', 'DB 없음 · Redis :6380 사용', 'mem 2GiB · cpu 2 · read_only'], 'business-api · /actuator :9091')
    box(d, 'data', 655, 580, 'Data · app:8080', ['내부 권한·도메인 명령·정산', '제품 상태 + outbox 같은 TX', 'PostgreSQL · Shared Redis · 1536MiB', '→ Meta CAPI HTTPS · 켠 경우만'], 'app = data-api · /actuator :9091')
    box(d, 'realtime', 1240, 580, 'Realtime · :8081', ['WSS /ws/realtime · 내부 REST', '채팅 DB · 이동·presence·fanout', 'Data에 현재 권한 조회', 'mem 768MiB · Shared Redis :6379'], 'realtime · /actuator :9091', 'event')
    box(d, 'gateway', 70, 880, '관리 전용 nginx', ['사설 :18080 → app · :18082 → noti', '공지·잡지·정책·발행 관리 경로만', '꾸미기 현황·추첨 풀·지급 경로 없음', '신고 관리 경로 없음 · SG: 백오피스만'], 'backoffice-gateway · app-network')
    box(d, 'notification', 655, 880, 'Notification · :8082', ['내부 HTTP: 기기·설정·관리', 'Kafka 사건 소비 → FCM HTTPS', '알림 DB · 중복·발송·재시도', 'mem 768MiB'], 'notification · /actuator :9091', 'event')
    box(d, 'localObs', 1240, 880, '앱 호스트 관측 컨테이너', ['Datadog Agent 512MiB · app-network', 'Fluent Bit 256MiB · host network', 'Loki 512MiB · observability network', 'Grafana: 구성 있음 · OFF'], '수집·저장 흐름은 04절 / 로그 도면', 'external')
    edge(d, 'publicHttp', 'nginx', 'business', [(1370,415),(1370,455),(50,455),(50,620),(70,620)], '허용한 공개 HTTP', (760,445))
    edge(d, 'publicWs', 'nginx', 'realtime', [(1570,415),(1570,580)], 'WSS', (1570,554))
    edge(d, 'bizData', 'business', 'data', [(520,645),(655,645)], 'HTTP', (588,635))
    edge(d, 'bizChat', 'business', 'realtime', [(420,770),(420,795),(1450,795),(1450,770)], 'Business → Realtime 내부 채팅 REST', (1170,785))
    edge(d, 'dataEvents', 'data', 'realtime', [(1105,645),(1240,645)], '사건 HTTP', (1172,635))
    edge(d, 'realtimeAuth', 'realtime', 'data', [(1240,705),(1105,705)], '권한 조회', (1172,695))
    edge(d, 'bizNoti', 'business', 'notification', [(520,735),(600,735),(600,945),(655,945)], '기기·설정 HTTP', (600,808))
    edge(d, 'adminData', 'gateway', 'data', [(490,880),(490,835),(880,835),(880,770)], '관리 HTTP :18080 → :8080', (910,825))
    edge(d, 'adminNoti', 'gateway', 'notification', [(520,1010),(655,1010)], ':18082', (588,1000))

    d.band(40, 1140, 1680, 510, '03 · 호스트 간 저장소 연결 · 동일 서비스를 호출 주체로 다시 표시',
           'EC2 간에는 VPC 사설 IP 사용. 아래 app-network들은 호스트마다 별개이며 하나의 분산 Docker 네트워크가 아니다.')
    box(d, 'sqlClients', 70, 1230, 'Data · Realtime · Notification', ['각 서비스 JDBC → 자신의 DB', 'Business는 DB에 직접 연결하지 않음'], 'PostgreSQL TCP :5432', h=135)
    box(d, 'eventClients', 655, 1230, 'Data relay · Notification 소비자', ['알림: notification-events · DLT', 'Realtime Kafka 소비는 선택 경로'], 'Kafka TCP :9092', 'event', h=135)
    box(d, 'redisClients', 1240, 1230, 'Data·Realtime / Business', ['Shared: presence·fanout·이동 상태', 'Business: 폐기 세션 등 전용 키'], 'Shared :6379 / Business :6380', h=135)
    box(d, 'rds', 70, 1440, '기존 RDS · catus-prod-db', ['db.t4g.small · PostgreSQL :5432', 'gromo / gromo_chat / gromo_notification', '별도 catus-prod-db-v2는 미사용'], '물리 인스턴스 공유 · 논리 DB 분리', 'data')
    box(d, 'kafka', 655, 1440, 'catus-kafka-prod-V2', ['m6g.medium · Kafka 3.8.1', '1 broker + controller · RF 1', '사설 :9092 · controller :9093 내부', '/var/lib/catus-V2/kafka 영속 저장'], 'SG: app 호스트 → :9092', 'event')
    box(d, 'redis', 1240, 1440, 'catus-redis-prod-V2', ['m6g.medium · Redis 7.4.11 두 개', ':6379→6379 / :6380→6379', 'maxmemory 384 / 128MiB · noeviction', 'AOF · ACL · shared/business 경로 분리'], 'SG: app 호스트 → :6379 / :6380', 'data')
    for ident, src, dst, x, label in [('jdbc','sqlClients','rds',295,'JDBC :5432'),('broker','eventClients','kafka',880,':9092'),('redisTcp','redisClients','redis',1465,':6379 / :6380')]:
        edge(d, ident, src, dst, [(x,1365),(x,1440)], label, (x,1410))

    d.band(40, 1690, 1680, 410, '04 · 로그·APM·지표 · 앱과 수집기가 같은 호스트 자원을 사용',
           '11/03 확인: 네 서버·nginx S3 적재 / Fluent Bit·Loki running / Grafana OFF. Datadog SaaS 수신은 별도다.')
    box(d, 'sources', 70, 1790, '실제 수집 입력', ['네 JVM: JSON stdout + DD tracer', 'nginx: JSON access / stderr error', 'Docker json-file: 50MiB × 4', '기타 3호스트: 각자 Datadog Agent'], 'Data user-activity 파일은 별도 경로', h=230)
    box(d, 'collectors', 655, 1790, '두 수집 경로', ['Datadog: Docker 로그·APM·지표', 'APM :8126 / DogStatsD UDP :8125', 'OpenMetrics: 각 앱 :9091 allowlist', 'Fluent Bit: 허용한 앱·nginx만 tail', 'fluent_bit_state: offset·디스크 버퍼'], '앱 stdout 파일을 두 수집기가 각각 읽음', 'external', h=230)
    box(d, 'sinks', 1240, 1790, '검색·보관', ['Datadog SaaS: 로그·APM·지표', 'Loki: 127.0.0.1:3100 · 로컬 7일', 'S3: system_log/v2/ · 만료 90일', 'Grafana OFF · 조회는 로그 안내 참고', 'user-activity: 파일 업로더 미설치 확인'], '11/03 S3 객체 확인 · 상세 도면: 로그·추적', 'data', h=230)
    edge(d, 'collectLogs', 'sources', 'collectors', [(520,1890),(655,1890)], '각각 수집', (588,1880))
    edge(d, 'storeLogs', 'collectors', 'sinks', [(1105,1890),(1240,1890)], '분기 전송', (1172,1880))

    d.band(40, 2140, 1680, 390, '05 · 백오피스의 별도 호스트와 관리 경로',
           '백오피스가 DB로 직접 들어가지 않고 앱 호스트의 관리 프록시를 거친다. Cloudflare 뒤 Origin TLS는 앱과 별도다.')
    box(d, 'operator', 70, 2240, '운영자 브라우저', ['backoffice-v2.oneorthree.world', 'HTTPS → Cloudflare → nginx :443', '구 backoffice 주소는 302 이동'], '운영자 인증', 'external')
    box(d, 'backoffice', 655, 2240, 'catus-backoffice-prod-V2', ['t4g.small · nginx → app:4310', '/var/lib/catus-V2/backoffice → /state', '별도 Datadog Agent · APM OFF', '일일 상태 백업 → S3'], '백오피스 UI와 로컬 상태')
    box(d, 'adminTargets', 1240, 2240, '앱 호스트 관리 프록시', ['사설 :18080 → Data :8080', '사설 :18082 → Notification :8082', 'allowlist에 꾸미기·신고 관리 없음', '공개 nginx의 /internal은 404'], '02절 backoffice-gateway 재표시')
    edge(d, 'consoleWeb', 'operator', 'backoffice', [(520,2330),(655,2330)], '443', (588,2320))
    edge(d, 'consoleInternal', 'backoffice', 'adminTargets', [(1105,2330),(1240,2330)], '사설 HTTP', (1172,2320))

    d.band(40, 2570, 1680, 400, '06 · 개발 환경은 GCP V2 · 운영과 다른 배치',
           'oneorthree-v2.dev.mooo.com · main 자동 CD · 11-05~06 새 GCP 프로젝트, 같은 VM. dev에는 Datadog Agent·백오피스 없음.')
    box(d, 'devApp', 70, 2670, 'catus-dev-v2-app · e2-medium', ['nginx + 서버 4종', '운영과 같은 서비스 경계', 'data VM · redis VM에 사설 연결'], '개발 앱 호스트')
    box(d, 'devData', 655, 2670, 'catus-dev-v2-data · e2-small', ['PostgreSQL 16.14 :5432', 'Kafka 3.8.1 :9092 · RF 1', '운영 RDS·Kafka와 다른 배치'], '개발 DB + broker', 'data')
    box(d, 'devRedis', 1240, 2670, 'catus-dev-v2-redis · e2-micro', ['Shared·Business Redis 7.4.11', ':6379 / :6380 · ACL · AOF', '운영보다 작은 메모리 한도'], '개발 Redis', 'data')
    edge(d, 'devDb', 'devApp', 'devData', [(520,2760),(655,2760)], '사설 TCP', (588,2750))
    edge(d, 'devRedisTcp', 'devApp', 'devRedis', [(295,2860),(295,2920),(1465,2920),(1465,2860)], '앱 → Redis 사설 TCP', (880,2910))

    d.band(40, 3010, 1680, 400, '07 · 공개 3D 웹 · AWS 밖 별도 배치',
           '정적 웹은 Vercel, 실시간 방은 Cloudflare Worker. Cattus 서버 4종·AWS와 연결선이 없다. 배포 문서 기준.')
    box(d, 'webVisitor', 70, 3110, '웹 방문자 브라우저', ['try.oneorthree.world', '앱 계정·집중 기록과 분리된 체험', '새로고침·종료 때 방 집중·예약 해제'], '설치 없는 체험', 'external')
    box(d, 'webStatic', 655, 3110, 'Vercel · 정적 3D 웹', ['정적 빌드 파일만 배포', '해시 번들·에셋 1년 캐시', 'Cattus 서버 API 호출 없음'], 'app/metaverse-web', 'external')
    box(d, 'webRoom', 1240, 3110, 'Cloudflare Worker · 방', ['Durable Object IslandRoom 하나', 'WSS /island-room · Origin 1개만', '두 섬 합계 60명 · 낚시 의자 30석'], '방 주소는 배포 때 빌드에 지정', 'event')
    edge(d, 'webHttps', 'webVisitor', 'webStatic', [(520,3195),(655,3195)], 'HTTPS', (588,3185))
    edge(d, 'webWss', 'webStatic', 'webRoom', [(1105,3195),(1240,3195)], 'WSS', (1172,3185))
    return d


def logging():
    d = frame('06-logging', 'Cattus · 로그 수집·보관·요청 추적', 3220)
    d.band(40, 140, 1680, 400, '01 · 앱 호스트의 입력 · 로그와 trace는 다른 데이터',
           'JVM·nginx stdout을 Docker가 파일로 기록한다. APM trace와 지표는 Docker 로그를 거치지 않고 Agent로 전달된다.')
    box(d, 'jvm', 70, 240, 'Business·Data·Realtime·Noti', ['ObservationJsonProvider → stdout', 'schema_version=1 · log_id · timestamp', 'service / env / version / log_kind', 'request_id · dd.trace_id · 사건 ID', '허용 필드·민감값 마스킹·크기 제한'], 'prod JSON · Business는 access 로그 포함', h=230)
    box(d, 'nginxLogs', 655, 240, 'nginx · access / error', ['access: JSON → /dev/stdout', 'edge_request_id / upstream_request_id', 'method · uri · status · request_time', 'query·요청 헤더·client IP 제외', 'error: /dev/stderr · warn 이상'], 'Fluent Bit에서 정규화·경로 정제', h=230)
    box(d, 'docker', 1240, 240, 'Docker json-file', ['/var/lib/docker/containers/', '<id>/<id>-json.log', '앱·nginx: max-size 50m × 4', '두 수집기에 read-only mount', '회전 파일 .1 등은 Fluent Bit tail 제외'], '유한한 호스트 버퍼 · 장기 보관소 아님', 'data', h=230)
    edge(d, 'stdout', 'jvm', 'docker', [(295,470),(295,510),(1465,510),(1465,470)], 'stdout/stderr → Docker 파일', (880,500))
    edge(d, 'nginxStdout', 'nginxLogs', 'docker', [(1105,340),(1240,340)], 'stdout', (1172,330))

    d.band(40, 580, 1680, 480, '02 · 독립 수집기 · Datadog → Fluent Bit 직렬 연결이 아님',
           'APM 8126/TCP · DogStatsD 8125/UDP · OpenMetrics 9091/TCP. 호스트 지표는 Agent가 /proc·cgroup에서 읽는다.')
    box(d, 'ddAgent', 70, 680, '앱 Datadog Agent · 512MiB', ['Docker 파일에서 로그 수집', 'JVM tracer → :8126 APM', 'JVM runtime → :8125 UDP', 'Agent → 앱 :9091/actuator/prometheus', '허용한 Micrometer 지표만 수집', 'JVM 부팅 잡음 필터는 DD 경로에만'], 'app-network · DD_SITE 기본 us5', 'external', h=270)
    box(d, 'fluent', 655, 680, 'Fluent Bit 4.2.8 · 256MiB', ['host network · Docker 파일 read-only', 'catus-app-v2 프로젝트만 허용', 'app → data-api 이름 매핑', '네 서버·nginx 외 컨테이너 drop', 'JSON parse / raw·nginx 정제·마스킹', 'fluent_bit_state: tail.db + 버퍼', 'Loki 원본 + S3 복제본을 따로 전송'], 'tail → Lua → parser → Lua → outputs', 'external', h=270)
    box(d, 'hostAgents', 1240, 680, 'Kafka·Redis·백오피스 Agent', ['각 EC2에 별도 Datadog Agent', '각 호스트 Docker 로그·호스트 지표', 'APM OFF · Agent 한도 256MiB', 'Redis :6379/:6380 health 계정 체크', '이 세 호스트는 Fluent Bit 경로 없음', 'Kafka JMX 별도 체크는 미설정'], '11/02 Agent health PASS 기록', 'external', h=270)
    edge(d, 'dockerDd', 'docker', 'ddAgent', [(1340,470),(1340,560),(50,560),(50,790),(70,790)], 'Docker 로그', (360,550))
    edge(d, 'dockerFluent', 'docker', 'fluent', [(1560,470),(1560,655),(880,655),(880,680)], 'Docker 로그', (1190,665))
    edge(d, 'tracer', 'jvm', 'ddAgent', [(70,400),(20,400),(20,665),(295,665),(295,680)], 'APM·runtime 지표', (155,671))

    d.band(40, 1100, 1680, 490, '03 · 목적지와 보관 한도',
           '11/03: S3 서비스별 최신 객체 확인 · Loki running · Loki 최신 수신은 별도 확인')
    box(d, 'datadog', 70, 1210, 'Datadog SaaS', ['Agent → HTTPS 전송', '로그·trace·호스트·컨테이너 지표', '로그에서 dd.trace_id로 APM 연결', '보관 기간: 조직 설정에서 확인', 'dev V2에는 Agent 없음'], 'Agent healthy ≠ SaaS 최신 수신', 'external', h=250)
    box(d, 'loki', 655, 1210, 'Loki 3.3.2 · 로컬 7일', ['Fluent Bit → 127.0.0.1:3100', '별도 observability network', 'loki_data → /loki · 단일 인스턴스', 'retention 168h + compactor ON', '라벨은 env / service / log_kind', 'ID는 JSON 필드로 조회'], 'app-network에 미연결 · 인증 없는 API', 'data', h=250)
    box(d, 's3', 1240, 1210, 'S3 · system_log/v2/', ['gzip JSONL · env/service/date/hour', '10MiB 또는 5분 단위 업로드', '앱 EC2 IAM: prod 접두 쓰기만', '로그 만료 규칙: 90일', 'Loki 청크 저장소가 아닌 별도 아카이브', '객체 파티션 시간 = 첫 레코드 시각'], '11/03 서비스별 S3 객체 확인 · retry 60', 'data', h=250)
    edge(d, 'agentSaas', 'ddAgent', 'datadog', [(295,950),(295,1075),(50,1075),(50,1280),(70,1280)], 'HTTPS', (295,1065))
    edge(d, 'otherAgentSaas', 'hostAgents', 'datadog', [(1465,950),(1465,1040),(30,1040),(30,1310),(70,1310)], '다른 3호스트 로그·지표', (1090,1030))
    edge(d, 'lokiOutput', 'fluent', 'loki', [(880,950),(880,1210)], ':3100', (880,1175))
    edge(d, 's3Output', 'fluent', 's3', [(1105,870),(1170,870),(1170,1175),(1465,1175),(1465,1210)], '복제 → S3 HTTPS', (1430,1165))

    d.band(40, 1630, 1680, 400, '04 · 조회 도구·수집 한계·빠진 범위',
           '점선 상자는 OFF 또는 업로더 미설치 경로다. 사용자 행동 로그와 시스템 stdout을 같은 수집 범위로 보지 않는다.')
    box(d, 'grafana', 70, 1730, 'Grafana · OFF', ['구성은 있으나 배포 스위치 false', '활성화 시 Loki datasource 사용', 'Cloudflare Access JWT · JWKS/aud', '현재 Grafana 접속 주소 없음'], '대신 Datadog / 승인된 Loki 접근 사용', 'future', 'off', h=230)
    box(d, 'buffer', 655, 1730, '유실·지연을 판별할 지점', ['Loki 엔진 버퍼 128MiB', 'S3 엔진 64MiB + store_dir 64MiB', '상한·회전·재시도 소진 시 유실 가능', 'canary 60초 간격 · 목적지별 도착 확인', 'canary 도착 ≠ 모든 앱 로그 수집 성공'], '기존 canary 관찰 · 새 트래픽 생성 불필요', 'external', h=230)
    box(d, 'ua', 1240, 1730, 'Data user-activity · 별도 파일', ['additivity=false · stdout에 안 섞임', '/app/logs/user-activity.log', '호스트 /var/log/catus-V2/data-api', '로컬 30일 · 1GiB cap', '11/03 호스트: 파일 업로더 미설치'], 'V2 버킷에 사용자 행동 객체 없음', 'future', 'off', h=230)
    edge(d, 'grafanaQuery', 'grafana', 'loki', [(295,1730),(295,1540),(880,1540),(880,1460)], '활성화할 때 Loki 조회', (610,1530), 'off')

    d.band(40, 2070, 1680, 660, '05 · 장애 한 건을 연결하는 키 · 수집 경로와 별개의 논리 흐름',
           'request_id는 HTTP 상관키, dd.trace_id는 APM, event_id는 사건, log_id는 로그 한 건의 식별자다.')
    box(d, 'httpIds', 70, 2170, 'HTTP → Business → Data', ['Business가 request_id 생성', '응답 X-Request-Id / 내부 호출 전파', 'nginx upstream_request_id와 연결', 'dd.trace_id는 실제 tracer context'], 'request_id를 APM trace ID로 쓰지 않음')
    box(d, 'eventIds', 655, 2170, 'outbox → Kafka/HTTP', ['event_id를 전달·재시도 동안 유지', 'origin_request_id / origin_trace_id', '새 consumer trace와 원요청을 연결', 'outbox.delivery → consumer.accept'], '저장한 carrier context를 비동기로 전파', 'event')
    box(d, 'deliveryIds', 1240, 2170, 'Notification → FCM', ['operation.link → transport.result', '→ dispatch.settle', 'operation_id / delivery_id / attempt', 'FCM 성공 ≠ 기기 도착'], 'dispatch.settle은 delivery_id+attempt', 'event')
    edge(d, 'httpEvent', 'httpIds', 'eventIds', [(520,2260),(655,2260)], '원인 저장', (588,2250))
    edge(d, 'eventDelivery', 'eventIds', 'deliveryIds', [(1105,2260),(1240,2260)], '사건 소비', (1172,2250))
    box(d, 'fanoutIds', 70, 2460, 'Realtime · Redis fanout', ['fanout.publish → fanout.receive', 'message_id / origin trace context', '인스턴스 간 사건을 연결'], 'Pub/Sub 전달은 영속 재생 로그 아님', 'event')
    box(d, 'queryIds', 655, 2460, 'Loki · 최근 로그 조회', ['env/service/log_kind로 범위 제한', '| json → request_id / event_id 필터', '같은 log_id 사본은 자동 제거 안 됨'], 'Grafana OFF여도 Loki API는 별도 존재', 'data')
    box(d, 'archiveQuery', 1240, 2460, 'S3 · Athena SQL 템플릿', ['env/service/date/hour 먼저 제한', '본문 timestamp로 최종 범위 필터', '수집 지연 구간은 시간 파티션 확대'], 'DDL·SQL 준비됨 · Athena 적용 미확인', 'data')

    d.band(40, 2770, 1680, 400, '06 · 앱 오류 수집 · 서버 로그 경로와 별개',
           '모바일 앱의 오류·크래시는 Sentry, JS 오류 일부는 PostHog로 간다. Datadog·Loki·S3를 거치지 않는다.')
    box(d, 'appErrors', 70, 2870, '모바일 앱 · 오류 SDK', ['Sentry SDK: JS 오류·네이티브 크래시', 'PostHog: JS 오류만 수집', '구버전 Android OTA만 PostHog 네이티브'], '@sentry/react-native · posthog-react-native', 'external')
    box(d, 'appBuild', 655, 2870, '운영 빌드 · Gradle·Xcode', ['JS 소스맵 업로드', 'Android mapping·네이티브 심볼', 'iOS dSYM', 'SENTRY_AUTH_TOKEN 있을 때만'], '#1575 도입 · #1671 누락 보완')
    box(d, 'errorSaas', 1240, 2870, 'Sentry · PostHog', ['Sentry: 오류·크래시 이벤트', '올린 심볼로 스택 복원', 'PostHog: JS 오류 · 제품 이벤트와 함께'], '외부 SaaS · 앱 서버 Agent와 무관', 'external')
    edge(d, 'appErrorSend', 'appErrors', 'errorSaas', [(295,3060),(295,3110),(1465,3110),(1465,3060)], '오류·크래시 전송', (880,3100))
    edge(d, 'symbolUpload', 'appBuild', 'errorSaas', [(1105,2955),(1240,2955)], '심볼', (1172,2945))
    return d
