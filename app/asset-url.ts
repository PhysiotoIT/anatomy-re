/** Resolve atlas files under the same base path as the built application. */
export function assetUrl(path:string):string {
 return `${import.meta.env.BASE_URL}${path.replace(/^\/+/, '')}`;
}
