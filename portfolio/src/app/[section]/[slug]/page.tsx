import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { docSections, findSection } from "@root/site.config";
import { getDoc, getDocs, getHeadings, getSiblings } from "@/lib/content";
import { Callout } from "@/components/callout";
import { Mdx } from "@/components/mdx";
import { PrevNext } from "@/components/prev-next";
import { SectionRail } from "@/components/section-rail";
import { StatusPill } from "@/components/status-pill";
import { Toc } from "@/components/toc";

export const dynamicParams = false;

export function generateStaticParams() {
  return docSections.flatMap((section) =>
    getDocs(section.slug).map((doc) => ({ section: section.slug, slug: doc.slug })),
  );
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ section: string; slug: string }>;
}): Promise<Metadata> {
  const { section, slug } = await params;
  const doc = getDoc(section, slug);
  if (!doc) return {};
  return {
    title: doc.title,
    description: doc.summary,
    openGraph: { title: doc.title, description: doc.summary, type: "article" },
  };
}

/**
 * Document page.
 *
 * This is the layout the two clones disagreed about, merged: PokeClip's sticky
 * section rail and prev/next on the left and bottom, FillMap's accent-railed
 * summary above the body, and the table of contents neither of them put on a
 * document page.
 */
export default async function DocPage({
  params,
}: {
  params: Promise<{ section: string; slug: string }>;
}) {
  const { section: sectionSlug, slug } = await params;
  const section = findSection(sectionSlug);
  const doc = getDoc(sectionSlug, slug);
  if (!section || section.kind !== "docs" || !doc) notFound();

  const docs = getDocs(sectionSlug);
  const headings = getHeadings(doc.body);
  const { prev, next } = getSiblings(sectionSlug, slug);

  return (
    <div className="mx-auto grid max-w-6xl gap-10 px-6 py-14 lg:grid-cols-[15.5rem_minmax(0,1fr)] xl:grid-cols-[15.5rem_minmax(0,1fr)_13.5rem]">
      <aside className="hidden lg:block">
        <SectionRail section={section} docs={docs} activeSlug={slug} />
      </aside>

      <article className="min-w-0">
        <Link
          href={`/${section.slug}`}
          className="inline-block font-mono text-[0.6875rem] uppercase tracking-[0.1em] text-muted-foreground no-underline hover:text-primary lg:hidden"
        >
          ← {section.title}
        </Link>

        <header className="mt-3 lg:mt-0">
          <h1 className="text-[1.9rem] font-bold leading-[1.25] tracking-[-0.02em]">
            {doc.title}
          </h1>

          {(doc.author || doc.status || doc.date || doc.keywords.length > 0) && (
            <ul className="mt-4 flex flex-wrap items-center gap-2">
              {doc.author && (
                <li className="text-[0.8125rem] font-medium text-muted-foreground">
                  {doc.author}
                </li>
              )}
              {doc.status && (
                <li>
                  <StatusPill status={doc.status} />
                </li>
              )}
              {doc.date && (
                <li>
                  <time
                    dateTime={doc.date}
                    className="rounded-pill border border-border px-2 py-[0.15rem] font-mono text-[0.6875rem] tabular-nums text-muted-foreground"
                  >
                    {doc.date}
                  </time>
                </li>
              )}
              {doc.keywords.map((keyword) => (
                <li
                  key={keyword}
                  className="rounded-pill border border-border px-2 py-[0.15rem] font-mono text-[0.6875rem] text-muted"
                >
                  {keyword}
                </li>
              ))}
            </ul>
          )}
        </header>

        {doc.summary && (
          <div className="mt-6">
            <Callout>{doc.summary}</Callout>
          </div>
        )}

        <div className="mt-4 rounded-card border border-border bg-surface-1 p-4 text-sm leading-6 text-muted-foreground">
          {doc.recordType === "current" ? (
            <p>
              {doc.date} 기준 안내입니다.
              {doc.sourceCommit && <> 근거: <a className="text-primary underline" href={`https://github.com/OneOrThree/phone/tree/${doc.sourceCommit}`}>phone main {doc.sourceCommit.slice(0, 9)}</a>.</>}
              {" "}코드 확인과 운영 배포·실기기 확인은 문서에서 구분합니다.
            </p>
          ) : (
            <p>
              {doc.recordType === "decision" ? "당시의 설계 결정 기록입니다. 후속 결정이 있으면 아래 적용 범위를 먼저 확인하세요." : "당시의 기록입니다. 본문의 날짜·수치·완료 상태는 해당 시점에 한정됩니다."}
              {" "}<Link className="text-primary underline" href="/spec/current-state">현재 Cattus 안내</Link>
              {" · "}<Link className="text-primary underline" href="/operations/06-v2-deployment">현재 V2 운영·배포</Link>
            </p>
          )}
          {sectionSlug === "performance" && <p className="mt-2">AWS 부하 테스트의 실행·재개와 부하용 데이터 생성은 금지되어 있습니다. 이 절은 보관한 결과를 읽는 용도이며 V2의 현재 수용량을 보증하지 않습니다.</p>}
        </div>

        {headings.some((heading) => heading.depth === 2) && (
          <nav aria-label="내용 바로가기" className="mt-6 rounded-card border border-border p-4">
            <details open>
              <summary className="cursor-pointer font-semibold">내용 바로가기</summary>
              <ul className="mt-3 grid gap-x-5 gap-y-2 text-sm sm:grid-cols-2">
                {headings.filter((heading) => heading.depth === 2).map((heading) => (
                  <li key={heading.id}><a href={`#${heading.id}`} className="text-primary underline underline-offset-4">{heading.text}</a></li>
                ))}
              </ul>
            </details>
          </nav>
        )}

        <div className="doc-prose mt-8">
          <Mdx source={doc.body} />
        </div>

        {doc.related.length > 0 && (
          <section className="mt-12 rounded-card border border-border bg-surface-1 px-4 py-4">
            <h2 className="font-mono text-[0.6875rem] uppercase tracking-[0.1em] text-muted-foreground">
              관련 문서
            </h2>
            <ul className="mt-2.5 space-y-1.5">
              {doc.related.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="text-sm text-primary underline underline-offset-[3px]"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </section>
        )}

        <PrevNext prev={prev} next={next} />
      </article>

      <aside className="hidden xl:block">
        <Toc headings={headings} />
      </aside>
    </div>
  );
}
