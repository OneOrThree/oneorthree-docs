#!/usr/bin/env python3
"""2026-11-03 phone main 대조 도면. 이전 버전은 최초 실행 때만 보존한다."""
import importlib
import json
from shutil import copy2

reviewed = importlib.import_module('make-reviewed-architecture-diagrams')
base = reviewed.base
ROOT = base.ROOT
COMMIT = 'af80af04241cefaa33b9f2a1e383548ecc9b10fa'
VERSIONS = {'01-ia': 6, '02-journey': 6, '03-service': 7, '04-system': 8, '05-cloud': 3, '06-logging': 1}
base.TARGET_VERSIONS.update(VERSIONS)
reviewed.COMMIT = COMMIT


def diagram(name, title):
    return base.Diagram(name, title, '2026.11.03 · phone main af80af042 · 코드와 저장소 운영 기록 대조 · 새 운영 실측 아님', 1220)


def band(d, row, title, subtitle):
    d.band(40, 140 + row * 340, 1680, 310, title, subtitle)


def node(d, ident, row, col, title, lines, stage, kind='core'):
    reviewed.box(d, ident, 70 + col * 585, 230 + row * 340, 450, 190, title, lines, kind, stage)


def across(d, ident, source, target, row, col, label):
    x = 520 + col * 585
    y = 315 + row * 340
    d.edge(ident, source, target, [(x,y),(x+135,y)], label, (x+67,y-10), state='code')


def down(d, ident, source, target, row, col, label):
    x = 295 + col * 585
    y = 420 + row * 340
    d.edge(ident, source, target, [(x,y),(x,y+150)], label, (x,y+42), state='code')


def ia():
    d=diagram('01-ia','Cattus · 정보 구조')
    band(d,0,'진입과 섬 생활','게스트·소셜 계정, 주민·섬장·방문자와 시설 조건을 구분한다.')
    node(d,'entry',0,0,'시작·계정',['게스트 또는 소셜 로그인','닉네임·고양이 모습·온보딩','친구 요청·편지·구매는 소셜 필요'],'현재 앱')
    node(d,'home',0,1,'섬 홈',['현재 섬·메인 섬','주민·방문자 상태','건물과 주민·이동'],'제품 중심 화면')
    node(d,'focus',0,2,'집중·휴식',['낚시섬 집중·모닥불 휴식','현재 세션 복구·응원','유효 집중 → 섬 물고기'],'Data 정산 · Realtime 표시')
    across(d,'entryHome','entry','home',0,0,'진입')
    across(d,'homeFocus','home','focus',0,1,'집중')
    band(d,1,'일곱 건물','건설 권한과 구매·조회 권한은 서로 다르다.')
    node(d,'manage',1,0,'마을회관·게시판',['건설 목표·공동 가계부·주민 관리','공지·퀘스트·청사진·방명록','건설 목표·착공은 섬장만'],'게스트 섬장도 건설 가능')
    node(d,'life',1,1,'도서관·축음기·상점',['내 일기장·이웃 일기장','보유 음악 재생·꾸미기 구매','가격·상품 발행·시설 조건'],'공동 구매: 주민 · 게스트 제외')
    node(d,'outside',1,2,'우체통·전망대',['친구 편지·시스템 편지·잡지','섬 주간 순위·검색','친구 편지와 단체 채팅은 별도'],'기능별 시설·권한 검사')
    down(d,'homeLife','home','life',0,1,'시설')
    band(d,2,'연락·탐색·플랫폼','현재 제품 용어와 기능별 전송 경로를 사용한다.')
    node(d,'chat',2,0,'친구·우리 섬 채팅방',['친구 관계·차단·비동기 편지','단체 채팅 REST 전송·조회','전경·활성 화면에서 10초 폴링'],'편지: Data · 채팅: Realtime')
    node(d,'travel',2,1,'뗏목·먼바다',['망원경에서 행선지 선택','항해·도착·섬에 내리기','고양이 잡지·섬 홍보'],'이동 프레임과 제품 정본 분리')
    node(d,'settings',2,2,'설정·네이티브 기능',['iOS 허용 앱·실드','Android 측정·위젯·일반 푸시','Android 집중 차단은 제거됨'],'네이티브 변경은 새 바이너리')
    return d


def journey():
    d=diagram('02-journey','Cattus · 사용자 여정')
    band(d,0,'매일의 집중','화면 타이머가 보상 정본을 대신하지 않는다.')
    node(d,'enter',0,0,'01 · 섬에 들어가기',['계정·고양이·닉네임','주민 자격과 현재 섬 확인','방문자는 구경 권한 사용'],'게스트로도 시작 가능')
    node(d,'start',0,1,'02 · 집중하기',['낚시섬에서 집중 시작','집중 상태·응원·이동 표시','필요하면 모닥불에서 휴식'],'서버의 현재 세션 기준')
    node(d,'finish',0,2,'03 · 마치고 확인하기',['유효 집중 구간 정산','휴식 시간은 적립에서 제외','섬 통장과 기록 확인'],'개인 물고기 지갑 없음')
    across(d,'enterStart','enter','start',0,0,'시작')
    across(d,'startFinish','start','finish',0,1,'종료')
    band(d,1,'공동 성장','목표 선택은 차감 0. 착공할 때 잔액과 조건을 검사한다.')
    node(d,'wallet',1,0,'04 · 물고기 모으기',['집중·퀘스트 등 도메인별 적립','원장·멱등성은 서버가 판정','잔액과 기록의 날짜 축 구분'],'섬 통장 소유')
    node(d,'build',1,1,'05 · 건설하기',['섬장이 다음 건물 목표 선택','물고기로 착공 → 공사 중 → 완공','동시 공사·선행 시설 조건 검사'],'게스트 섬장도 가능')
    node(d,'use',1,2,'06 · 시설 이용하기',['도서관·음악·편지·순위·상점','활성 주민의 공동 구매','구매는 소셜 로그인 필요'],'상품 발행·가격은 별도 조건')
    across(d,'walletBuild','wallet','build',1,0,'잔액')
    across(d,'buildUse','build','use',1,1,'완공')
    band(d,2,'다음 방문으로 이어지는 활동','단체 채팅·친구 편지·항해는 각각의 권한과 복구 경로를 따른다.')
    node(d,'talk',2,0,'연락하기',['친구 요청·편지 발송: 소셜 필요','단체 채팅: 섬 주민 자격','차단·시설 조건은 기능별 판정'],'편지와 채팅은 다른 API')
    node(d,'sail',2,1,'항해하기',['뗏목에서 목적지 선택','먼바다 집중·도착·하선','섬 발견·가입으로 연결'],'바다 세션과 이동 구분')
    node(d,'return',2,2,'다시 이어하기',['앱 복귀 시 서버 상태 조회','이동 재입장은 FullState 복구','이전 측정값과 현재 세션 구분'],'연결 생존 ≠ 집중 정본')
    return d


def service():
    d=diagram('03-service','Cattus · 서비스 아키텍처')
    band(d,0,'공개 HTTP와 제품 정본','Business는 공개 계약, Data는 현재 권한·원자 명령·제품 데이터의 정본을 맡는다.')
    node(d,'app',0,0,'모바일 앱',['React Native · Expo','공개 HTTP · /screens 조합 응답','WSS는 Realtime 연결'],'활성 2.0 앱')
    node(d,'business',0,1,'Business API',['공개 인증·DTO·오류·화면 조합','Data·Realtime·Notification 호출','Business Redis: 폐기 sid'],'도메인 DB 없음')
    node(d,'data',0,2,'Data API · 코어 DB',['섬·집중·물고기·상품·친구·편지','현재 주민 자격·원장·receipt','PostgreSQL 상태·outbox'],'친구 편지는 letters에 저장')
    across(d,'http','app','business',0,0,'HTTP')
    across(d,'internal','business','data',0,1,'내부 HTTP')
    band(d,1,'채팅과 실시간','현재 앱의 단체 채팅은 REST·10초 폴링. STOMP의 채널별 권한은 별도다.')
    node(d,'chatApp',1,0,'앱 · 우리 섬 채팅방',['Business → Data 주민 자격 확인','Business → Realtime 내부 REST','clientMessageId로 재전송 처리'],'저장 후 사건 기록은 별도 TX')
    node(d,'realtime',1,1,'Realtime · 채팅 DB',['채팅 저장·조회·fanout','집중·휴식·응원·섬 사건','이동·바다·폐기 세션 처리'],'gromo_chat · 채팅 정본','event')
    node(d,'shared',1,2,'Shared Redis',['presence·chat fanout','이동 lease·epoch·명령·프레임','이동 multi-instance 기본 ON'],'제품 권한·영속 이동 로그 아님','data')
    across(d,'chatRest','chatApp','realtime',1,0,'내부 REST')
    across(d,'redis','realtime','shared',1,1,'전파·상태')
    band(d,2,'커밋된 사건과 알림','전달 성공·소비 성공·기기 도착은 각각 다른 단계다. 플래그 기본값과 운영값도 구분한다.')
    node(d,'outbox',2,0,'Data · outbox relay',['상태와 사건을 같은 TX로 기록','대상별 전달·중복·재시도','세션 폐기는 Realtime에도 전달'],'채팅 저장과는 별도 호출')
    node(d,'transport',2,1,'Kafka · 내부 HTTP',['알림: notification-events','REALTIME: 기본 HTTP','realtime-events는 선택 경로'],'소비자 활성화는 개별 설정','event')
    node(d,'notification',2,2,'Notification · 알림 DB',['수신·중복 방지·발송 조건','기기 설정·발송 이력','FCM으로 외부 푸시 요청'],'gromo_notification','event')
    across(d,'relay','outbox','transport',2,0,'전달')
    across(d,'notify','transport','notification',2,1,'알림 사건')
    down(d,'realtimeEvent','realtime','transport',1,1,'사건 입구')
    # Direction: transport sends the event to Realtime.
    e=d.edges[-1];e['source'],e['target']=e['target'],e['source'];e['points'].reverse()
    return d


def system():
    return importlib.import_module('make-runtime-diagrams').system()


def logging():
    return importlib.import_module('make-runtime-diagrams').logging()


def cloud():
    d=diagram('05-cloud','Cattus · AWS 운영 V2')
    band(d,0,'공개 진입과 서버','현재 배치는 저장소 운영 기록 기준이며 이 도면 자체가 호스트 가용성 검사는 아니다.')
    node(d,'client',0,0,'앱·운영자',['앱: catus-api-v2 도메인','운영자: backoffice-v2 도메인','HTTPS·WSS 공개 경로'],'*.oneorthree.world','external')
    node(d,'edge',0,1,'Cloudflare·nginx',['공개 주소·TLS·라우팅','HTTP는 Business로 전달','WSS는 Realtime으로 전달'],'내부 API는 앱 진입점 아님','external')
    node(d,'app',0,2,'서버 EC2 · m6g.large',['Business·Data·Realtime·Notification','서비스별 이미지·설정·DB 계약','nginx와 서버 4종 한 호스트'],'catus-prod-V2')
    across(d,'edgeEntry','client','edge',0,0,'HTTPS/WSS')
    across(d,'appEntry','edge','app',0,1,'라우팅')
    band(d,1,'분리한 런타임과 저장소','Kafka와 Redis는 각자 EC2. RDS는 기존 운영 인스턴스를 계속 사용한다.')
    node(d,'kafka',1,0,'Kafka · m6g.medium',['Kafka 3.8.1','알림 사건과 선택 REALTIME 경로','별도 발행·수동 CD'],'catus-kafka-prod-V2','event')
    node(d,'redis',1,1,'Redis · m6g.medium',['Redis 7.4.11 두 인스턴스','Shared maxmemory 384MB','Business maxmemory 128MB'],'noeviction · AOF · ACL','data')
    node(d,'db',1,2,'RDS PostgreSQL',['catus-prod-db · db.t4g.small','서비스별 데이터 소유권','별도 catus-prod-db-v2는 미사용'],'마이그레이션 배포 게이트','data')
    down(d,'appDb','app','db',0,2,'DB')
    band(d,2,'운영 지원과 변경 경로','운영 기록의 Agent health와 Datadog 최신 수신 상태는 구분한다.')
    node(d,'backoffice',2,0,'백오피스 · t4g.small',['공지·운영진 편지·잡지·정책','서버·앱 출시 현황','main → 환경 승인 → 배포'],'catus-backoffice-prod-V2')
    node(d,'artifacts',2,1,'ECR·S3·SSM',['이미지 digest·불변 릴리스','deployments 성공 상태 기록','SSM으로 지정한 버전 적용'],'Infra revision 고정','external')
    node(d,'observability',2,2,'관측',['운영 4호스트 Datadog Agent','11월 2일 health 확인 기록','로그 rollout·수신은 별도 확인'],'V1 로그 경로와 구분','external')
    return d


def main():
    manifest=json.loads((ROOT/'diagrams/manifest.json').read_text())
    for d in (ia(),journey(),service(),system(),cloud(),logging()):
        version=VERSIONS[d.name]
        entry=next(e for e in manifest if e['id']==d.name)
        if entry['versions'][0]['id'] != f'v{version}':
            raise SystemExit(f'{d.name}: manifest 현재 버전 v{version} 등록 필요')
        if d.name=='05-cloud':
            source = ROOT/'diagrams'/f'{d.name}.source.json'
            source_version = json.loads(source.read_text())['version'] if source.exists() else None
            for suffix in ('svg','drawio.xml','source.json'):
                current=ROOT/'diagrams'/f'{d.name}.{suffix}'
                archived=ROOT/'diagrams'/f'{d.name}.v{source_version}.{suffix}'
                if source_version is not None and source_version < version and current.exists() and not archived.exists(): copy2(current,archived)
            d.write(archive=False)
            (ROOT/'diagrams'/f'{d.name}.source.json').write_text(json.dumps({'version':version,'sourceCommit':COMMIT,'title':d.title,'nodes':d.nodes,'edges':d.edges},ensure_ascii=False,indent=2)+'\n')
        else:
            reviewed.VERSION=version
            reviewed.write_html(d)


if __name__=='__main__':main()
