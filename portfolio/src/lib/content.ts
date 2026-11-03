import fs from "node:fs";
import path from "node:path";
import matter from "gray-matter";
import GithubSlugger from "github-slugger";

import type { SectionConfig } from "@root/site.config";
import { docSections, findSection } from "@root/site.config";

/**
 * The single source of truth for every document in the site.
 *
 * The section index, the sticky left rail, prev/next, the sitemap and llms.txt
 * all read from here, so dropping one `.mdx` file into `content/` wires it into
 * all of them. That is the whole difference between this template and the
 * cloned sites, where each of those lists was a separate hand-maintained array.
 */

const CONTENT_DIR = path.join(process.cwd(), "content");

export interface DocLink {
  label: string;
  href: string;
}

export interface Doc {
  section: string;
  slug: string;
  href: string;
  title: string;
  /** Rendered as the accent-railed callout above the body. */
  summary?: string;
  /** Free-form label shown as a pill: 유효 / 검토됨 / 대체됨 → ADR-004 … */
  status?: string;
  /** ISO date, e.g. "2026-08-05". */
  date?: string;
  /** Historical records retain their original dates; current guides cite a snapshot. */
  recordType: "current" | "historical" | "decision";
  sourceCommit?: string;
  /** Who wrote it. Shown on the index row and the document header. */
  author?: string;
  keywords: string[];
  /** Lower sorts first within a section. See `SectionConfig.sort`. */
  order?: number;
  related: DocLink[];
  body: string;
}

export interface Heading {
  depth: 2 | 3;
  text: string;
  id: string;
}

function readSectionDocs(section: string): Doc[] {
  const dir = path.join(CONTENT_DIR, section);
  if (!fs.existsSync(dir)) return [];

  const docs = fs
    .readdirSync(dir)
    .filter((f) => f.endsWith(".mdx"))
    .map((file) => {
      const slug = file.replace(/\.mdx$/, "");
      const raw = fs.readFileSync(path.join(dir, file), "utf8");
      const { data, content } = matter(raw);

      if (typeof data.title !== "string" || data.title.trim() === "") {
        throw new Error(
          `content/${section}/${file}: frontmatter is missing a "title".`,
        );
      }

      return {
        section,
        slug,
        href: `/${section}/${slug}`,
        title: data.title,
        summary: typeof data.summary === "string" ? data.summary : undefined,
        status: typeof data.status === "string" ? data.status : undefined,
        date: typeof data.date === "string" ? data.date : undefined,
        recordType: data.recordType === "current" ? "current" : section === "adr" ? "decision" : "historical",
        sourceCommit: typeof data.sourceCommit === "string" ? data.sourceCommit : undefined,
        author: typeof data.author === "string" ? data.author : undefined,
        keywords: Array.isArray(data.keywords) ? data.keywords.map(String) : [],
        order: typeof data.order === "number" ? data.order : undefined,
        related: Array.isArray(data.related)
          ? (data.related as DocLink[]).filter(
              (r) => r && typeof r.label === "string" && typeof r.href === "string",
            )
          : [],
        body: content,
      } satisfies Doc;
    });

  const mode = findSection(section)?.sort ?? "curated";
  return docs.sort((a, b) => compareDocs(a, b, mode));
}

type SortMode = NonNullable<SectionConfig["sort"]>;

function compareDocs(a: Doc, b: Doc, mode: SortMode): number {
  // Newest first, and a missing date sorts last rather than to the top.
  if (mode === "date" && a.date !== b.date) {
    if (!a.date) return 1;
    if (!b.date) return -1;
    return b.date.localeCompare(a.date);
  }
  return byCuratedOrder(a, b, mode === "curated-desc" ? -1 : 1);
}

/**
 * `direction` is 1 for ascending `order` and -1 for descending.
 *
 * A missing `order` goes last either way, so the sign is applied only to the
 * comparison between two documents that both have one. Reversing the whole
 * comparison instead would float an `order`-less document to the top of a
 * descending section, which is the opposite of what "no position given" means.
 */
function byCuratedOrder(a: Doc, b: Doc, direction: 1 | -1 = 1): number {
  if (a.order !== undefined || b.order !== undefined) {
    if (a.order === undefined) return 1;
    if (b.order === undefined) return -1;
    if (a.order !== b.order) return (a.order - b.order) * direction;
  }
  if (a.date && b.date && a.date !== b.date) return b.date.localeCompare(a.date);
  return a.title.localeCompare(b.title, "ko");
}

// Content never changes within a build, and every page reads these lists, so
// parse each section once.
const cache = new Map<string, Doc[]>();

export function getDocs(section: string): Doc[] {
  let docs = cache.get(section);
  if (!docs) {
    docs = readSectionDocs(section);
    cache.set(section, docs);
  }
  return docs;
}

export function getDoc(section: string, slug: string): Doc | undefined {
  return getDocs(section).find((d) => d.slug === slug);
}

export function getAllDocs(): Doc[] {
  return docSections.flatMap((s) => getDocs(s.slug));
}

/** Previous/next within the section, in the same order the left rail shows. */
export function getSiblings(
  section: string,
  slug: string,
): { prev?: Doc; next?: Doc } {
  const docs = getDocs(section);
  const i = docs.findIndex((d) => d.slug === slug);
  if (i === -1) return {};
  return { prev: docs[i - 1], next: docs[i + 1] };
}

/**
 * Table of contents for the right rail.
 *
 * Slugs come from the same `github-slugger` that `rehype-slug` uses on the
 * rendered headings, and a slugger instance is stateful about duplicates — so
 * a fresh one per document keeps "제목", "제목-1" in step with the anchors that
 * actually land in the HTML.
 */
export function getHeadings(body: string): Heading[] {
  const slugger = new GithubSlugger();
  const headings: Heading[] = [];
  let inFence = false;

  for (const line of body.split("\n")) {
    if (/^\s*(```|~~~)/.test(line)) {
      inFence = !inFence;
      continue;
    }
    if (inFence) continue;

    const m = /^(#{2,3})\s+(.+?)\s*$/.exec(line);
    if (!m) continue;

    // Strip inline markdown so the rail reads like the heading looks.
    const text = m[2]
      .replace(/`([^`]+)`/g, "$1")
      .replace(/\*\*([^*]+)\*\*/g, "$1")
      .replace(/\*([^*]+)\*/g, "$1")
      .replace(/\[([^\]]+)\]\([^)]*\)/g, "$1")
      .trim();

    headings.push({
      depth: m[1].length === 2 ? 2 : 3,
      text,
      id: slugger.slug(text),
    });
  }

  return headings;
}

export function getSectionOrThrow(slug: string) {
  const section = findSection(slug);
  if (!section) throw new Error(`Unknown section "${slug}" — add it to site.config.ts.`);
  return section;
}
