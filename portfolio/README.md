# OneOrThree · Cattus 문서 사이트


## 바로가기

| 작업 | 내용 |
| --- | --- |
| 실행·문서 | [시작하기](#시작하기) · [문서 추가](#문서-추가하기) |
| 그림 | [다이어그램 추가](#다이어그램-추가하기) · [Cattus 갱신](#cattus-다이어그램-갱신) · [버전 보존](#아키텍처-버전-보존) |
| 데이터 | [기여도](#팀-기여도-스냅샷-갱신) · [발전 기록](#발전-기록-자동-생성) |
| 게시 | [운영 기록](#운영트러블슈팅-기록) · [배포](#배포-vercel) · [검증](#검증할-때-주의) |

Cattus의 현재 안내와 팀의 과거 기록을 함께 공개합니다. Next.js 15 App Router와 Tailwind v4를 사용하며, 문서는 정적 생성하고 비밀번호로 보호한 갈등관리 페이지는 동적으로 제공합니다.

## 시작하기

```bash
npm ci
npm run dev          # http://localhost:3000
```

| 명령                | 하는 일                             |
| ------------------- | ----------------------------------- |
| `npm run dev`       | 다이어그램 빌드 후 개발 서버        |
| `npm run build`     | 다이어그램 빌드 후 정적 생성        |
| `npm run typecheck` | `tsc --noEmit`                      |
| `npm run verify`    | 뜬 서버에 전 라우트 요청해 200 확인 |

## 문서 추가하기

`content/<섹션>/<슬러그>.mdx` 파일 하나를 만들면 끝이다. 섹션 인덱스, 좌측 레일, 이전/다음, `sitemap.xml`, `llms.txt`가 전부 자동으로 따라온다.

```mdx
---
title: "ADR-003 — 제목" # 필수
summary: "본문 위 요약 박스에 들어갈 한두 문장"
status: "유효" # 유효/검토됨/대체됨 … 색은 단어에서 추론
date: "2026-11-03"
recordType: "current" # 현재 안내만 명시. 생략하면 ADR은 결정 기록, 나머지는 시점 기록
sourceCommit: "af80af04241cefaa33b9f2a1e383548ecc9b10fa" # phone 근거 커밋
order: 3 # 없으면 date 내림차순 → 제목순
keywords: ["키워드", "키워드"]
related:
  - label: "관련 문서"
    href: "/spec/architecture"
---

## 맥락

## 선택지

## 결정

## 근거

## 영향
```

`##`/`###` 제목은 자동으로 앵커가 붙고 우측 목차에 올라간다. 본문에서 `<Callout>` 과 `<StatusPill>` 을 바로 쓸 수 있다.

**섹션을 추가하려면** `site.config.ts` 의 `sections` 배열에 한 줄 넣고 `content/` 아래 같은 이름의 폴더를 만든다. 내비·랜딩 인덱스·sitemap이 알아서 반영한다.

## 다이어그램 추가하기

원본은 Google Drive의 draw.io다. 두 파일을 `diagrams/` 에 넣는다.

1. draw.io에서 **File → Export as → SVG** — "Include a copy of my diagram" **해제** → `diagrams/<id>.svg`
2. draw.io에서 **File → Save as → .drawio (XML)** → `diagrams/<id>.drawio.xml`
3. `diagrams/manifest.json` 에 `{ "id", "title", "titleEn", "summary" }` 추가

> `03-service`, `04-system`, `05-cloud`는 GROMO 도면이다. `01-ia`, `02-journey`는 R61 HTML을 표시한다. `scripts/make-placeholder-diagrams.mjs`는 전체 도면을 덮어쓰므로 기존 도면을 갱신할 때 실행하지 않는다.

`npm run build` 가 `scripts/build-diagrams.mjs` 를 돌려 `public/diagrams/` 에 셋을 만든다: 주석이 주입된 SVG, 연결 그래프 JSON, 다운로드용 원본 XML.

**왜 XML도 필요한가.** draw.io의 SVG export는 셀마다 `data-cell-id` 는 남기지만 **어느 엣지가 무엇을 잇는지는 남기지 않는다** (FillMap 클론의 export 실측: `data-cell-id` 104개, source/target 0개). 연결 관계는 XML의 `<mxCell edge="1" source= target=>` 에만 있다. 빌드 단계가 이 둘을 `data-cell-id` ↔ `mxCell/@id` 로 조인해서 SVG에 연결 정보를 심고, 그래야 "요소를 클릭하면 연결된 것만 남는" 동작이 가능하다.

조인이 실패하면 **빌드를 실패시킨다.** 클릭이 안 되는 다이어그램은 스크린샷으로는 멀쩡해 보이기 때문이다.

그룹 처리와 누락된 SVG 요소의 빌드 실패 회귀 검증: `node --test scripts/build-diagrams.test.mjs`.

**다이어그램에는 목록 페이지가 없다.** 헤더의 "다이어그램"은 첫 다이어그램으로 바로 간다(`/diagrams` 는 리다이렉트만 한다). 전환은 그림 위의 번호 선택 pill이 제자리에서 처리한다.

**`다이어그램 / 문서 보기` 토글.** 문서 보기는 같은 그래프를 텍스트로 렌더한다 — 요소마다 나가는/들어오는 연결과 엣지 라벨. 별도로 쓰는 내용이 아니라 `.drawio.xml` 에서 뽑은 그래프 그대로다.

## Cattus 다이어그램 갱신

현재 IA·유저 저니 v6, 서비스·시스템 v7, AWS v3은 `scripts/make-current-diagrams.py`에서 생성합니다. 같은 노드·간선으로 SVG·draw.io XML·source JSON을 만들고 앞의 네 도면은 HTML도 생성합니다.

```bash
python3 scripts/make-current-diagrams.py
npm run build
```

기준 커밋은 phone `af80af042`입니다. main 코드와 저장소의 운영 기록을 대조한 도면이며 새 운영 실측이 아닙니다. 이전 R61 HTML과 서비스·시스템 v6, AWS v2는 버전 선택에서 볼 수 있습니다. 과거 생성기는 현재 버전의 원본이 아니며 실행하지 않습니다.

HTML의 동반 SVG/XML은 빌드가 연결 그래프·다운로드와 함께 검증합니다. 근거 문서는 manifest의 `detailHref`로 연결합니다.

### 아키텍처 버전 보존

모든 도면은 최신 파일을 덮어쓴 뒤 이전 파일을 지우지 않는다. SVG·draw.io 도면은 `<id>.v1.svg`와 `<id>.v1.drawio.xml`, HTML 도면은 `<id>.v1.html`처럼 보존하고 manifest의 `versions`에 `artifactId`, 날짜, 대체 사유, 근거 문서와 원본 커밋을 등록한다. 빌드는 SVG·draw.io 버전의 연결 그래프와 HTML 버전 파일을 모두 만들며, 페이지의 버전 선택은 도면·문서 보기·설계 뷰·다운로드 원본을 함께 전환한다.

버전이 하나뿐인 도면도 `versions`를 생략하지 않는다. 현재 별칭(`<id>`)을 새 버전으로 바꾸기 전에 기존 파일을 명시적 버전(`<id>.vN`)으로 먼저 보존한다.

manifest는 최신 버전을 맨 앞에 두고, 최신 항목만 현재 별칭(`<id>`)을 사용한다. 이전 버전은 반드시 `<id>.vN`이라는 독립 파일을 가리킨다. 빌드는 순서가 뒤집히거나 현재 별칭을 이전 버전이 재사용하면 실패한다.

### 공통 시각 문법

`04-system`을 모든 현재 다이어그램의 시각 기준으로 사용한다. 흰 캔버스, 32px 제목과 17px 부제, `#f8fafc` 영역 밴드, 12px 모서리의 의미별 카드, `#607583` 2px 연결선, `Apple SD Gothic Neo, Noto Sans KR, sans-serif` 글꼴을 공통으로 쓴다. 유스케이스처럼 구조가 다른 도면도 같은 토큰과 제목 계층을 유지한다. 과거 IA·유저 저니 v4·v5는 R61 원본의 시각 문법을 보존합니다.

현재 도면을 고칠 때는 먼저 생성기의 `TARGET_VERSION` 또는 `TARGET_VERSIONS`를 올리고 manifest에 새 현재 버전과 이전 버전을 함께 등록한다. 생성기는 직전 현재 별칭을 해당 버전 파일로 한 번만 보존하며, 같은 버전으로 다시 실행해도 보존본을 덮어쓰지 않는다.

현재 생성기는 도면별 `VERSIONS`를 사용합니다. HTML은 직전 버전, SVG/XML/source JSON은 확인된 실제 생성 버전으로 보존합니다. 이전 R61 HTML과 같은 이름의 오래된 SVG를 같은 판으로 간주하지 않습니다.

## 운영·트러블슈팅 기록

`content/operations/`는 prod 사고·dev 장애·CI 문제의 영향·진단 근거·복구·재발 방지를 연결한다. 기존 연구 노트의 본문은 보존하고 사례 지도에서 해당 기록과 티켓을 연결한다. 실제 사용자가 받은 영향과 코드 리뷰·감사에서 발견한 위험은 구분한다. 원문에 없는 MTTR·사용자 수·개선율은 추가하지 않으며 임시 복구·근본 대책·운영 적용·재검증을 같은 완료 상태로 합치지 않는다.

현재 v1은 문서 저장소의 `345aa78`(2026-09-08)에서 복원했고, v2는 2026-09-13의 Kafka·Redis 경계 반영본이다.

## 이전 R61 유스케이스

R61 기획 HTML은 IA·유저 저니의 v1~v5에서 보존합니다. `sync-r61-html.py`와 과거 제품 생성기는 당시 복원용입니다. 현재 그림을 바꿀 때는 위의 Cattus 생성기와 `content/spec/use-cases.mdx`를 함께 고칩니다.

## 팀 기여도 스냅샷 갱신

`src/data/contributions.json`은 GitHub에서 조회한 **머지 PR의 assignee**만 사람별로 센다. 커밋 작성자와 PR 작성자는 사용하지 않으며, assignee가 없는 PR은 미배정으로 따로 남긴다. 현재 `back/`과 `server/` 경로를 모두 포함해 영역을 분류한다. PR 건수와 함께 파일별 변경 줄 수(락파일·`.json`·이미지 등 `NOISE_SUFFIXES` 제외)를 영역별로 더하고, 이 사이트 `content/`의 문서 수를 frontmatter `author`로 센다. `contributions.mdx`·`roles.mdx`의 수치는 `<Contrib>`·`<ContributionTable>`이 JSON에서 직접 읽으므로 손으로 고치지 않는다.

```bash
python3 scripts/sync-contributions.py
```

`gh` 로그인과 `OneOrThree/phone` 읽기 권한이 필요하다. 생성된 JSON을 커밋한다. Jira는 별도 인증 조회가 필요하며 이 스크립트는 Jira 수치를 생성하지 않는다.

## 발전 기록 자동 생성

`src/data/evolution.json`은 직접 편집하지 않는다. 생성기가 `phone` 저장소 `origin/main`의 first-parent 기록에서 `docs/`, `.github/workflows/`, `server/scripts/` 변경만 모아 날짜·제목·SHA·변경 파일을 기록한다.

```bash
npm run sync:evolution
npm run check:evolution
```

기본 source 경로는 이 저장소와 나란히 있는 `../phone`이다. 다른 위치에서는 `GROMO_SOURCE_REPO=/path/to/phone`을 지정한다. `predev`와 `prebuild`도 source 저장소가 보이는 환경에서는 자동으로 갱신하고, Vercel처럼 source가 없는 환경에서는 커밋된 스냅샷을 그대로 사용한다.

## 기술 회고 추가

`content/retrospective/`에 회고를 추가한다. 회고는 목표, Keep, Problem, Try, Action item, 근거 순서로 작성하고, 회의 기록이 없으## HTML 다이어그램의 표시

IA와 유저 저니는 설계 쪽 R61 HTML 원본(`gachisup-R61-assets/문서/IA-R61.html`, `User-Journey-R61.html`)을 사이트용으로 가공합니다. `diagrams/01-ia.html`, `diagrams/02-journey.html`이 가공 결과이고 manifest 항목에 `"format": "html"`을 지정합니다. 빌드가 이를 `public/diagrams/`에 복사하고 `/diagrams/01-ia`, `/diagrams/02-journey` 페이지는 독립 프레임으로 표시합니다. 프레임 상단의 별도 제목줄은 두지 않으며(위 선택기와 버전 버튼이 제목 역할) "새 창에서 보기" 링크는 프레임 아래에 있습니다.

원본이 바뀌면 다음을 실행합니다. 원본 위치가 다르면 `GROMO_R61_DOCS`로 지정합니다.

```bash
python3 scripts/sync-r61-html.py
npm run build
```

가공 내용: IA 원본의 제목·부제·푸터와 외부 문서 링크(상세 명세 MD, 정책 문서, 근거 파일), 데이터에 남은 로컬 절대경로를 제거합니다. IA는 `주요 기능`·`세부 기능 펼침` 버튼과 범례(개인·소셜·혼합·공통, 실선/점선)만 한 줄에 남기고 구역 선택·검색·화면 맞춤·SVG 저장은 숨깁니다(스크립트가 참조하므로 삭제 대신 CSS). 유저 저니는 v4의 흐름도 형식과 개인·소셜 강조 인터랙션을 유지하고 최신 문구·정책만 반영하며, 프레임 높이에 맞춰 자동 축소합니다. 원본 draw.io(`User-Journey-R61.drawio`)와 SVG(`IA-R61-tree.svg`, `User-Journey-R61-overview.svg`)는 참고용으로 `02-journey.drawio.xml`, `02-journey.svg`, `01-ia.svg`에 같이 두고, IA draw.io는 원본에 없어서 `scripts/make_ia_drawio.py`가 트리 데이터와 SVG 좌표로 `01-ia.drawio.xml`을 생성합니다. HTML 형식이라 draw.io·SVG는 빌드가 읽지 않고 배포하지도 않습니다. 별도 명세 문서는 함께 배포하지 않습니다.

새 버전을 낼 때는 버전 보존 규칙대로 현재 파일을 `<id>.vN.html`로 먼저 보존하고 manifest `versions` 맨 앞에 새 항목을 넣은 뒤 스크립트를 실행합니다. `public/diagrams/`는 빌드 때 다시 생성되므로 직접 편집하지 않습니다.

하지 않습니다. `public/diagrams/`는 빌드 때 다시 생성되므로 직접 편집하지 않습니다.

## 브랜드 바꾸기

- 이름·문구·내비·스택: `site.config.ts`
- 색: `src/styles/tokens.css` 의 `--primary` 한 줄. 나머지는 파생된다. 라이트/다크 각각 정의돼 있다.

## 배포 (Vercel)

1. 이 저장소를 Vercel 프로젝트로 임포트
2. **Root Directory** 를 `portfolio` 로 지정
3. `DEPLOY_ENABLED=1`을 배포 환경에 설정합니다. `vercel.json`의 ignoreCommand가 이 값 없이는 빌드를 건너뜁니다.
4. `NEXT_PUBLIC_SITE_ORIGIN`으로 절대 URL을 설정할 수 있습니다. 기본값은 `https://docs.oneorthree.world`입니다.

프레임워크·빌드 명령은 자동 감지된다. `prebuild` 가 다이어그램을 만들므로 별도 설정은 없다.

## 검증할 때 주의

`npm run verify`는 경로의 HTTP 상태를 확인합니다. 추가로 `node --test scripts/build-diagrams.test.mjs`를 실행하고 문서 목차·내부 링크·버전별 그림과 모바일 화면을 확인합니다. HTTP 상태 검사는 하이드레이션 단계에서만 터지는 클라이언트 예외는 잡지 못한다 — 실제로 이 템플릿 개발 중 `IntersectionObserver` 의 `rootMargin` 에 `rem` 을 써서 모든 문서 페이지가 죽었는데, 빌드·타입체크·200 검증이 전부 통과했다. 문서 페이지 하나와 다이어그램 하나는 브라우저에서 콘솔을 열고 확인할 것.

## 알려진 한계

- 다이어그램은 다크모드에서도 밝은 캔버스 위에 렌더한다. draw.io export가 `fill="#f1f2f4"` 같은 고정색을 갖기 때문. 도형 팔레트를 CSS 변수로 매핑하는 건 후속 작업.
- 문서 검색(Cmd+K)은 넣지 않았다.
- TypeScript는 5.x로 고정돼 있다. 7.x(네이티브 재작성)에서는 Next 15의 TS 감지가 실패해 경로 별칭이 통째로 깨진다.
