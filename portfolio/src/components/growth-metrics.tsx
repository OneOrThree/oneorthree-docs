import growthData from "@/data/growth.json";

/**
 * GA4 지표 블록 — 그로스 섹션 인덱스 상단.
 *
 * 데이터는 손으로 만들지 않는다. 수집 결과가 growth.json에 들어오면 기준일과 함께 표시한다.
 * 2026-11-03 저장소 스냅샷은 비어 있으며 자동 수집의 현재 가동 여부는 확인되지 않았다.
 *
 * 차트는 외부 라이브러리 없이 인라인 SVG다 — ContributionDonuts와 같은 규칙.
 */

interface Period {
  activeUsers: number;
  newUsers: number;
  sessions: number;
}

interface Growth {
  summary?: { main: Period; d7: Period; d30: Period; d90: Period };
  daily: { date: string; activeUsers: number; newUsers: number; sessions: number }[];
  dauMix: { date: string; newVsReturning: string; activeUsers: number }[];
  retention: { day: number; users: number }[];
  steps: { label: string; branch: boolean; users: number }[];
  activation: { label: string; users: number }[];
  propertyId?: string;
  start?: string;
  asOf?: string | null;
  generatedAt?: string | null;
}

// growth.json은 봇이 덮어쓰는 파일이라 초기 상태가 빈 배열이다. 그 모양에서 추론된
// never[]로는 아래 map이 서지 않으므로, ContributionDonuts와 같이 한 번 단언한다.
const g = growthData as unknown as Growth;

const SERIES = [
  { key: "new", label: "신규", color: "var(--chart-1)" },
  { key: "returning", label: "재방문", color: "var(--chart-2)" },
] as const;

/** GA4는 어제 수치를 1~2일 뒤에 확정한다 — 마지막 두 칸은 아직 올라가는 중이다. */
const PROVISIONAL = 2;

/** 막대가 읽히는 한계. 시작일이 고정이라 그냥 두면 칸이 무한히 얇아진다. */
const WINDOW = 56;

const mmdd = (iso: string) => iso.slice(5).replace("-", "/");

export function GrowthMetrics() {
  if (!g.asOf || !g.summary) {
    return (
      <section className="mb-12 rounded-card border border-dashed border-border px-5 py-8 text-center text-sm text-muted-foreground">
        최신 GA4 스냅샷이 없습니다. 아래 분석은 각 문서에 적힌 기간의 기록입니다.
        {" "}<a href="/growth/current-data-scope" className="text-primary underline">자료의 범위 확인하기</a>
      </section>
    );
  }

  const { main, d7, d30 } = g.summary;
  const steps = g.steps.filter((s) => !s.branch);
  const entered = steps[0]?.users ?? 0;
  const finished = steps.at(-1)?.users ?? 0;

  return (
    <section aria-labelledby="growth-heading" className="mb-14">
      <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
        <h2 id="growth-heading" className="text-[1.05rem] font-bold tracking-[-0.01em]">
          지금 숫자
        </h2>
        <p className="font-mono text-[0.6875rem] tabular-nums text-muted">
          {g.asOf} 기준 · {g.generatedAt?.slice(0, 16).replace("T", " ")} 갱신
        </p>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-3 lg:grid-cols-4">
        <Tile
          label="누적 신규 유저"
          value={main.newUsers}
          note={`${g.start}부터`}
        />
        <Tile
          label="활성 유저"
          value={d7.activeUsers}
          note={`최근 7일 · 30일 ${d30.activeUsers.toLocaleString()}`}
        />
        <Tile
          label="세션"
          value={d7.sessions}
          note={`최근 7일 · 1인당 ${ratio(d7.sessions, d7.activeUsers)}회`}
        />
        <Tile
          label="온보딩 완주율"
          value={entered ? Math.round((finished / entered) * 100) : 0}
          unit="%"
          note={`진입 ${entered.toLocaleString()} → 완주 ${finished.toLocaleString()}`}
        />
      </div>

      <DailyMix rows={g.dauMix} />
      <Activation rows={g.activation} />
      <Retention rows={g.retention} />

      <p className="mt-5 text-[0.75rem] leading-relaxed text-muted-foreground">
        GA4 속성 {g.propertyId} · 팀 계정과 안드로이드 비공개 테스터는 조회 단계에서
        제외합니다. <strong className="font-semibold text-foreground">마지막 이틀은 잠정치</strong>입니다 —
        GA4가 하루치를 확정하는 데 1~2일이 걸려 실제보다 낮게 잡힙니다.
      </p>
    </section>
  );
}

function ratio(a: number, b: number) {
  return b ? (a / b).toFixed(1) : "—";
}

function Tile({
  label,
  value,
  unit,
  note,
}: {
  label: string;
  value: number;
  unit?: string;
  note: string;
}) {
  return (
    <div className="rounded-card border border-border bg-surface-1 px-4 py-4">
      <p className="font-mono text-[0.625rem] uppercase tracking-[0.08em] text-muted">
        {label}
      </p>
      <p className="mt-1.5 font-mono text-[1.6rem] font-bold leading-none tabular-nums text-foreground">
        {value.toLocaleString()}
        {unit && <span className="text-[0.9rem] font-semibold">{unit}</span>}
      </p>
      <p className="mt-2 text-[0.75rem] leading-snug text-muted-foreground">{note}</p>
    </div>
  );
}

function Legend() {
  return (
    <ul className="flex items-center gap-3">
      {SERIES.map((s) => (
        <li
          key={s.key}
          className="flex items-center gap-1.5 text-[0.75rem] text-muted-foreground"
        >
          <span
            aria-hidden
            className="inline-block size-2 rounded-[2px]"
            style={{ backgroundColor: s.color }}
          />
          {s.label}
        </li>
      ))}
    </ul>
  );
}

function Block({
  title,
  legend,
  children,
  footnote,
}: {
  title: string;
  legend?: boolean;
  children: React.ReactNode;
  footnote?: string;
}) {
  return (
    <figure className="mt-6 rounded-card border border-border bg-surface-1 px-4 py-4 sm:px-5">
      <figcaption className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
        <span className="text-[0.875rem] font-semibold text-foreground">{title}</span>
        {legend && <Legend />}
      </figcaption>
      {children}
      {footnote && (
        <p className="mt-2 text-[0.75rem] leading-relaxed text-muted-foreground">
          {footnote}
        </p>
      )}
    </figure>
  );
}

/** 일별 활성 유저를 신규/재방문으로 쌓는다 — "하루의 주인이 누구인가". */
function DailyMix({ rows }: { rows: Growth["dauMix"] }) {
  const byDate = new Map<string, { new: number; returning: number }>();
  for (const r of rows) {
    const cell = byDate.get(r.date) ?? { new: 0, returning: 0 };
    if (r.newVsReturning === "new") cell.new += r.activeUsers;
    else cell.returning += r.activeUsers;
    byDate.set(r.date, cell);
  }
  const days = [...byDate.entries()].sort().slice(-WINDOW);
  if (days.length === 0) return null;

  const W = 720;
  const H = 168;
  const PLOT = 138; // 아래 30px은 날짜 눈금
  const max = Math.max(...days.map(([, c]) => c.new + c.returning), 1);
  const slot = W / days.length;
  const bar = Math.max(slot - 2, 1); // 막대 사이 2px 여백

  const y = (v: number) => PLOT - (v / max) * PLOT;

  return (
    <Block
      title="일별 활성 유저 — 신규와 재방문"
      legend
      footnote={`최근 ${days.length}일. 막대 높이는 그날 앱을 쓴 사람 수이고, 아래쪽이 그날 처음 온 사람입니다. 오른쪽 음영 두 칸은 GA4가 아직 확정하지 않은 잠정치입니다.`}
    >
      <svg
        viewBox={`0 0 ${W} ${H}`}
        className="mt-3 h-auto w-full"
        role="img"
        aria-label={`최근 ${days.length}일 일별 활성 유저 구성. 최고 ${max}명.`}
      >
        {/* 최댓값 기준선 */}
        <line x1="0" y1={y(max)} x2={W} y2={y(max)} stroke="var(--border)" strokeWidth="1" />
        <text x="2" y={y(max) - 4} className="fill-[var(--muted)] font-mono text-[10px]">
          {max}
        </text>

        {/* 아직 확정되지 않은 마지막 이틀. 설명은 아래 각주가 맡는다 — 이 폭에
            글자를 얹으면 그 이틀의 막대와 겹친다. */}
        {days.length > PROVISIONAL && (
          <rect
            x={(days.length - PROVISIONAL) * slot - 1}
            y="0"
            width={PROVISIONAL * slot}
            height={PLOT}
            fill="var(--surface-3)"
          />
        )}

        {days.map(([date, c], i) => {
          const x = i * slot + (slot - bar) / 2;
          const hNew = (c.new / max) * PLOT;
          const hRet = (c.returning / max) * PLOT;
          return (
            <g key={date}>
              <title>{`${date} · 활성 ${c.new + c.returning} (신규 ${c.new} · 재방문 ${c.returning})`}</title>
              {/* 재방문이 위, 신규가 아래. 둘 사이 2px은 표면색으로 띄운다. */}
              {c.returning > 0 && (
                <rect
                  x={x}
                  y={y(c.new + c.returning)}
                  width={bar}
                  height={Math.max(hRet - 2, 0.5)}
                  fill={SERIES[1].color}
                />
              )}
              {c.new > 0 && (
                <rect x={x} y={PLOT - hNew} width={bar} height={hNew} fill={SERIES[0].color} />
              )}
            </g>
          );
        })}

        <line x1="0" y1={PLOT} x2={W} y2={PLOT} stroke="var(--border-strong)" strokeWidth="1" />

        {days.map(([date], i) =>
          i % 7 === 0 ? (
            <text
              key={date}
              x={i * slot + slot / 2}
              y={PLOT + 16}
              textAnchor="middle"
              className="fill-[var(--muted)] font-mono text-[10px]"
            >
              {mmdd(date)}
            </text>
          ) : null,
        )}
      </svg>
    </Block>
  );
}

/** 앱을 처음 연 사람이 실제로 집중을 마치기까지 — 단계마다 몇 명이 남는가. */
function Activation({ rows }: { rows: Growth["activation"] }) {
  if (rows.length === 0) return null;
  const base = rows[0].users || 1;

  return (
    <Block
      title="활성화 퍼널 — 집중을 마치기까지"
      footnote={`${g.start} 이후 누적. 닫힌 퍼널이 아니라 단계별 도달 인원이라, 같은 사람이 여러 단계에 잡힙니다.`}
    >
      <ol className="mt-3 space-y-2.5">
        {rows.map((s) => {
          const pct = (s.users / base) * 100;
          return (
            <li key={s.label} className="grid grid-cols-[7.5rem_minmax(0,1fr)_3.5rem] items-center gap-3">
              <span className="text-[0.8125rem] leading-snug text-muted-foreground">
                {s.label}
              </span>
              <span className="h-2.5 rounded-[3px] bg-surface-3">
                <span
                  className="block h-full rounded-[3px]"
                  style={{ width: `${Math.max(pct, 1)}%`, backgroundColor: SERIES[0].color }}
                />
              </span>
              <span className="text-right font-mono text-[0.75rem] tabular-nums text-foreground">
                {s.users.toLocaleString()}
                <span className="ml-1 text-muted">{Math.round(pct)}%</span>
              </span>
            </li>
          );
        })}
      </ol>
    </Block>
  );
}

/** 가입한 날을 D0으로 놓고, 며칠째에 몇 명이 다시 오는가. */
function Retention({ rows }: { rows: Growth["retention"] }) {
  if (rows.length < 2) return null;
  const base = rows[0].users || 1;

  const W = 720;
  const H = 160;
  const PAD = 26;
  const PLOT = 104;
  const TOP = 24; // D0의 직접 라벨이 viewBox 위로 잘리지 않을 만큼
  const x = (i: number) => PAD + (i / (rows.length - 1)) * (W - PAD * 2);
  const y = (v: number) => TOP + PLOT - (v / base) * PLOT;

  const line = rows.map((r, i) => `${i === 0 ? "M" : "L"}${x(i)},${y(r.users)}`).join(" ");

  return (
    <Block
      title="리텐션 — 가입 다음 날부터 며칠째에 돌아오는가"
      footnote={`${g.start} 이후 가입자 ${base.toLocaleString()}명 기준. D0은 가입 당일입니다.`}
    >
      <svg
        viewBox={`0 0 ${W} ${H}`}
        className="mt-3 h-auto w-full"
        role="img"
        aria-label={rows
          .map((r) => `D${r.day} ${Math.round((r.users / base) * 100)}%`)
          .join(", ")}
      >
        <path
          d={`${line} L${x(rows.length - 1)},${y(0)} L${x(0)},${y(0)} Z`}
          fill={SERIES[0].color}
          opacity="0.1"
        />
        <path d={line} fill="none" stroke={SERIES[0].color} strokeWidth="2" />
        {rows.map((r, i) => (
          <g key={r.day}>
            <title>{`D${r.day} · ${r.users.toLocaleString()}명 (D0 대비 ${Math.round((r.users / base) * 100)}%)`}</title>
            <circle
              cx={x(i)}
              cy={y(r.users)}
              r="4"
              fill={SERIES[0].color}
              stroke="var(--surface-1)"
              strokeWidth="2"
            />
            <text
              x={x(i)}
              y={y(r.users) - 10}
              textAnchor="middle"
              className="fill-[var(--foreground)] font-mono text-[10px] font-semibold"
            >
              {Math.round((r.users / base) * 100)}%
            </text>
            <text
              x={x(i)}
              y={H - 4}
              textAnchor="middle"
              className="fill-[var(--muted)] font-mono text-[10px]"
            >
              D{r.day}
            </text>
          </g>
        ))}
      </svg>
    </Block>
  );
}
