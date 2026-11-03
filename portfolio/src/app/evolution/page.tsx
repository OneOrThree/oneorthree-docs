import type { Metadata } from "next";

import evolution from "@/data/evolution.json";
import { Kicker } from "@/components/kicker";

export const metadata: Metadata = {
  title: "발전 기록",
  description: "Cattus의 문서·배포·서버 실행 경로를 바꾼 phone main 최근 240개 커밋",
};

export default function EvolutionPage() {
  const months = new Map<string, typeof evolution.entries>();
  for (const entry of evolution.entries) {
    const month = entry.date.slice(0, 7);
    const entries = months.get(month) ?? [];
    entries.push(entry);
    months.set(month, entries);
  }

  return (
    <div className="mx-auto max-w-5xl px-6 py-16">
      <header className="max-w-3xl">
        <Kicker>EVOLUTION LOG</Kicker>
        <h1 className="mt-4 text-[2rem] font-bold leading-tight tracking-[-0.02em]">
          발전 기록
        </h1>
        <p className="mt-4 leading-relaxed text-muted-foreground">
          Cattus의 문서·배포·서버 실행 경로를 바꾼 main 최근 240개 커밋입니다.
          전체 제품 변경 목록은 아니며, 각 항목에서 기준 커밋과 변경 파일을 확인할 수 있습니다.
        </p>
      </header>

      <aside className="mt-8 rounded-card border border-border bg-primary-subtle px-5 py-4">
        <p className="font-semibold text-foreground">Git 로그에서 자동 생성</p>
        <p className="mt-1 text-sm leading-relaxed text-muted-foreground">
          <code className="font-mono text-xs">npm run sync:evolution</code>이 phone 저장소의
          first-parent 기록에서 <code className="font-mono text-xs">docs/</code>, 배포 워크플로,
          서버 실행 스크립트 변경을 읽습니다. 이 페이지의 항목을 손으로 추가하지 않습니다.
        </p>
        <p className="mt-2 font-mono text-[0.6875rem] text-muted">
          {evolution.source} · {evolution.entries.length} commits · source {evolution.generatedFrom?.slice(0, 7)}
        </p>
      </aside>

      <nav aria-label="월별 바로가기" className="mt-6 flex flex-wrap gap-4 text-sm">
        {[...months.keys()].map((month) => <a className="text-primary underline" key={month} href={`#month-${month}`}>{month}</a>)}
      </nav>

      <div className="mt-12 space-y-14">
        {[...months.entries()].map(([month, entries]) => (
          <section key={month} aria-labelledby={`month-${month}`}>
            <div className="flex items-baseline justify-between gap-4 border-b border-border pb-3">
              <h2 id={`month-${month}`} className="text-xl font-bold tabular-nums">
                {month}
              </h2>
              <span className="font-mono text-xs tabular-nums text-muted">{entries.length} changes</span>
            </div>

            <ol className="divide-y divide-border">
              {entries.map((entry) => (
                <li key={entry.sha} className="grid min-w-0 gap-3 py-5 sm:grid-cols-[5.5rem_minmax(0,1fr)] sm:gap-6">
                  <div>
                    <time dateTime={entry.date} className="font-mono text-xs tabular-nums text-muted-foreground">
                      {entry.date.slice(5)}
                    </time>
                    <span className="mt-1 block w-fit rounded-pill border border-border px-2 py-0.5 font-mono text-[0.625rem] text-muted">
                      {entry.category}
                    </span>
                  </div>
                  <div className="min-w-0">
                    <h3 className="font-semibold leading-relaxed text-foreground">{entry.subject}</h3>
                    <div className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-2">
                      <a
                        href={entry.href}
                        target="_blank"
                        rel="noreferrer noopener"
                        className="whitespace-nowrap font-mono text-xs text-primary no-underline hover:underline"
                      >
                        {entry.shortSha} ↗
                      </a>
                      <details className="text-xs text-muted-foreground">
                        <summary className="cursor-pointer whitespace-nowrap">변경 파일 {entry.files.length}개</summary>
                        <ul className="mt-2 space-y-1 border-l border-border pl-3 font-mono text-[0.6875rem] leading-relaxed">
                          {entry.files.map((file) => (
                            <li key={file}>{file}</li>
                          ))}
                        </ul>
                      </details>
                    </div>
                  </div>
                </li>
              ))}
            </ol>
          </section>
        ))}
      </div>
    </div>
  );
}
