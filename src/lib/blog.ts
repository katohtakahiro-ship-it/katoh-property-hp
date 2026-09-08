import { getCollection, type CollectionEntry } from 'astro:content';
import { localePath, otherLocale, type Locale } from '../i18n';

export type Post = CollectionEntry<'blog'>;

/** 記事 ID は 'ja/slug' / 'en/slug'（src/content/blog 配下のディレクトリ = ロケール） */
export const postLocale = (post: Post): Locale => post.id.split('/')[0] as Locale;
export const postSlug = (post: Post): string => post.id.split('/').slice(1).join('/');
export const postPath = (post: Post): string => localePath(postLocale(post), `/blog/${postSlug(post)}/`);

/** 指定ロケールの公開記事を新しい順で返す */
export async function getPosts(locale: Locale): Promise<Post[]> {
  const posts = await getCollection('blog', ({ id, data }) => !data.draft && id.startsWith(`${locale}/`));
  return posts.sort((a, b) => b.data.date.getTime() - a.data.date.getTime());
}

/** 対になる言語の記事があればそのパス、なければ null（hreflang と言語切替に使う） */
export async function getAlternatePath(post: Post): Promise<string | null> {
  const other = otherLocale(postLocale(post));
  const slug = postSlug(post);
  const candidates = await getCollection('blog', ({ id, data }) => !data.draft && id === `${other}/${slug}`);
  return candidates.length > 0 ? localePath(other, `/blog/${slug}/`) : null;
}
