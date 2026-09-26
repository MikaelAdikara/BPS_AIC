import { useEffect, useId, useState } from "react";
import { request, ApiError } from "@/api/http.js";
import { useWorkspace } from "@/api/workspace";
import { useI18n } from "@/lib/i18n";
import { Button, Field, LoadingState, Notice } from "@/components/ui";

export function DemoReview() {
  const { summary, busy, run } = useWorkspace();
  const { t, localizeError } = useI18n();
  const [products, setProducts] = useState<{ id: string; title: string }[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [revision, setRevision] = useState(0);
  const [product, setProduct] = useState("");
  const [rating, setRating] = useState("2");
  const [text, setText] = useState("");
  const id = useId();
  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setError(null);
    request("/deciqo/products?channel=woocommerce", { signal: controller.signal }).then(data => {
      if (!controller.signal.aborted) { setProducts(data.products); setProduct(current => data.products.some((item: {id:string}) => item.id === current) ? current : data.products[0]?.id ?? ""); }
    }).catch((e: ApiError) => { if (!controller.signal.aborted) setError(e.code); }).finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, [summary, revision]);
  if (loading) return <LoadingState />;
  return <form className="stack" onSubmit={event => {
    event.preventDefault();
    setError(null);
    void run(async () => {
      try { return await request("/deciqo/demo/reviews", {method:"POST", body:{product_id:product, rating:Number(rating), text}}); }
      catch(e) {setError((e as ApiError).code ?? "request_failed"); throw e;}
    }, "sources.synced", "sources.syncing");
  }}>
    {error && <Notice tone="alert" action={<Button variant="outline" onClick={()=>setRevision(value=>value+1)}>{t("common.retry")}</Button>}>{localizeError(error)}</Notice>}
    {products.length === 0 ? <p className="muted">{t("sources.demoEmpty")}</p> : <>
      <label htmlFor={id+"-product"}>{t("sources.product")}</label>
      <select id={id+"-product"} value={product} onChange={event=>setProduct(event.target.value)}>{products.map(item=><option key={item.id} value={item.id}>{item.title}</option>)}</select>
      <label htmlFor={id+"-rating"}>{t("sources.demoRating")}</label>
      <select id={id+"-rating"} value={rating} onChange={event=>setRating(event.target.value)}>{[1,2,3,4,5].map(value=><option key={value} value={value}>{value} ★</option>)}</select>
      <Field label={t("sources.demoText")} value={text} onChange={event=>setText(event.target.value)} required maxLength={2000} />
      <Button busy={busy} disabled={!text.trim()} type="submit">{t("sources.demoAdd")}</Button>
    </>}
  </form>;
}
