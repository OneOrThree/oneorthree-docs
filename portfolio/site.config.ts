/**
 * Every piece of site identity lives here.
 *
 * In both cloned sites the nav array was re-declared at the top of all ~30
 * `page.tsx` files, with the active item hand-flipped from `kind:"link"` to
 * `kind:"button"`. Adding a section meant editing thirty files. Here it means
 * adding one entry and one folder under `content/`.
 */

export type SectionKind = "docs" | "diagrams" | "generated";

export interface SectionConfig {
  /** URL segment, and the folder name under `content/` for `kind: "docs"`. */
  slug: string;
  /** Korean label shown in the header nav. */
  label: string;
  /** Monospace uppercase kicker above the index heading. */
  kicker: string;
  /** <h1> of the section index page. */
  title: string;
  /** One paragraph under the index heading, explaining what belongs here. */
  description: string;
  kind: SectionKind;
  /**
   * Put a search box on this section's index. Worth it where documents
   * accumulate; noise on a section that holds one or two.
   */
  search?: boolean;
  /**
   * How the index, the left rail and prev/next order this section.
   *
   * "curated" (default) follows the `order` field in each document's
   * frontmatter — right where a section is a reading sequence, like the
   * chronicle. "date" puts the newest document first, which is what a log of
   * decisions and notes should do; documents sharing a date fall back to
   * `order`, so a batch written on one day keeps its intended sequence.
   * "curated-desc" reverses `order` — for a numbered series where the number
   * is the identity and the newest entry has the highest one, like the ADRs.
   * Sorting those by date scatters the numbers (022 · 002 · 003 · 020 …)
   * because a revised ADR carries its revision date, not its decision date.
   *
   * A document with no `order` sorts last in every mode, including the
   * reversed one — absence should not win a ranking.
   */
  sort?: "curated" | "date" | "curated-desc";
}

export const sections: SectionConfig[] = [
  {
    slug: "diagrams",
    label: "다이어그램",
    kicker: "ARCHITECTURE DIAGRAMS",
    title: "다이어그램",
    description: "서비스의 정보 구조와 시스템 구성을 한눈에 살펴봅니다.",
    kind: "diagrams",
  },
  {
    slug: "spec",
    label: "설계·명세",
    kicker: "DESIGN & SPEC",
    title: "설계와 명세",
    description:
      "2026-11-03 phone main 기준의 Cattus 제품·서버·권한·운영 안내입니다. 구현과 배포 기록, 조건부 기능을 구분합니다.",
    kind: "docs",
    search: true,
    sort: "date",
  },
  {
    slug: "adr",
    label: "설계 결정",
    kicker: "DECISION RECORDS",
    title: "설계 결정 기록",
    description:
      "무엇을 정했는지가 아니라, 왜 그렇게 정했고 무엇을 기각했는지를 남깁니다. 뒤집힌 결정도 지우지 않고 대체됨으로 표시합니다.",
    kind: "docs",
    search: true,
    sort: "curated-desc",
  },
  {
    slug: "operations",
    label: "운영·트러블슈팅",
    kicker: "OPERATIONS & TROUBLESHOOTING",
    title: "운영과 트러블슈팅",
    description:
      "prod 사고와 dev·CI 장애를 구분해 영향·진단 근거·복구·재발 방지를 연결합니다. 임시 복구와 후속 검증 상태도 함께 남깁니다.",
    kind: "docs",
    search: true,
    sort: "curated",
  },
  {
    slug: "performance",
    label: "성능·부하",
    kicker: "LOAD TEST HISTORY",
    title: "부하테스트와 개선 기록",
    description:
      "2026년 7~10월에 보관한 측정·실패·개선 기록입니다. AWS 부하 테스트와 부하용 데이터 생성은 금지되어 있으며, 이 수치는 현재 V2 수용량을 보증하지 않습니다.",
    kind: "docs",
    search: true,
    sort: "curated",
  },
  {
    slug: "research",
    label: "연구 노트",
    kicker: "RESEARCH NOTES",
    title: "연구 노트",
    description:
      "당시 코드·측정·문제 해결의 근거를 보존합니다. 본문 날짜의 관측과 현재 Cattus 안내를 구분해 읽습니다.",
    kind: "docs",
    search: true,
    sort: "date",
  },
  {
    slug: "growth",
    label: "그로스",
    kicker: "GROWTH METRICS",
    title: "그로스 지표와 분석",
    description:
      "8~9월 Gromo 1.x의 주간 분석과 기능 조사를 보존합니다. 최신 GA4 스냅샷이 없어 현재 Cattus 지표는 제공하지 않습니다.",
    kind: "docs",
    search: true,
    sort: "date",
  },
  {
    slug: "evolution",
    label: "발전 기록",
    kicker: "EVOLUTION LOG",
    title: "발전 기록",
    description:
      "phone main에서 문서·배포·서버 실행 경로를 바꾼 최근 240개 커밋을 Git 로그로 모았습니다. 기준 커밋과 변경 파일을 함께 봅니다.",
    kind: "generated",
  },
  {
    slug: "retrospective",
    label: "회고",
    kicker: "RETROSPECTIVE",
    title: "기술 회고",
    description:
      "결과만 나열하지 않고, 유지할 것·문제가 된 것·다음에 시도할 것을 근거와 함께 남깁니다.",
    kind: "docs",
  },
  {
    slug: "history",
    label: "연대기",
    kicker: "PROJECT HISTORY",
    title: "프로젝트 연대기",
    description:
      "소프트웨어 마에스트로 시작부터 Gromo 출시, Cattus 재설계와 V2 전환까지를 기록합니다. 과거 회의·티켓과 최근 코드·운영 기록의 기준일을 구분합니다.",
    kind: "docs",
    search: true,
  },
  {
    slug: "team",
    label: "팀·역할",
    kicker: "TEAM & OWNERSHIP",
    title: "팀과 역할",
    description: "누가 무엇을 책임지고, 경계에서 어떤 계약을 주고받는지.",
    kind: "docs",
  },
];

export const docSections = sections.filter((s) => s.kind === "docs");

export const searchableSections = sections.filter((s) => s.search === true);

export function findSection(slug: string): SectionConfig | undefined {
  return sections.find((s) => s.slug === slug);
}

export const site = {
  /** Change these five lines to rebrand. */
  name: "OneOrThree",
  wordmark: "OneOrThree",
  subLabel: "CATTUS DOCS",
  tagline: "Cattus를 만드는 기록",
  description:
    "Cattus의 제품·아키텍처·운영 안내와 OneOrThree의 설계 결정, 실험, 성장 기록입니다.",

  /** Absolute origin for metadataBase, sitemap and robots. */
  origin: process.env.NEXT_PUBLIC_SITE_ORIGIN ?? "https://docs.oneorthree.world",

  hero: {
    kicker: "CATTUS · ONEORTHREE",
    headline: ["함께 집중하고,", "섬을 키우는 Cattus."],
    subline: "제품과 시스템, 바뀐 결정의 근거를 한곳에서.",
    lede: "2026-11-03 main 기준으로 제품·서버 4종·V2 운영을 안내합니다. 과거 결정과 실험은 당시 날짜와 수치를 보존하고 현재 안내로 연결합니다.",
    actions: [
      {
        label: "현재 안내부터 읽기",
        href: "/spec/current-state",
        variant: "solid" as const,
      },
      { label: "다이어그램 보기", href: "/diagrams", variant: "outline" as const },
      { label: "V2 운영·배포", href: "/operations/06-v2-deployment", variant: "outline" as const },
    ],
  },

  /** The "무엇으로 만들었나" strip on the landing page. */
  stack: [
    { name: "React Native · Expo", role: "iOS · Android 앱" },
    { name: "Next.js", role: "웹 · 문서" },
    { name: "Spring Boot", role: "서버 4종" },
    { name: "PostgreSQL", role: "주 저장소" },
    { name: "Redis", role: "전파 · 소유권 · 세션" },
    { name: "Kafka", role: "알림 · 선택 사건 경로" },
    { name: "AWS · GCP", role: "운영 V2 · dev V2" },
  ],

  footer:
    "현재 안내는 2026-11-03 main 기준입니다. 과거 기록은 각 문서의 날짜·환경·적용 범위와 함께 읽어 주세요.",
} as const;
