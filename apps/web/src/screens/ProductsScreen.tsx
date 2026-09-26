import { useEffect, useState } from "react";
import { request, ApiError } from "@/api/http.js";
import { useWorkspace } from "@/api/workspace";
import { useI18n } from "@/lib/i18n";
import {
  Button,
  Card,
  Chip,
  EmptyState,
  LoadingState,
  Notice,
  Table,
} from "@/components/ui";
interface Product {
  id: string;
  title: string;
  channel: string;
  synthetic: boolean;
  reviews: number;
  rating: number | null;
  findings: number;
  fixable: number;
  analysis_status: string;
  stale: boolean;
  engine: string | null;
}
export function ProductsScreen() {
  const { t, language, localizeError } = useI18n();
  const { summary, busy, run } = useWorkspace();
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [revision, setRevision] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setError(null);
    request("/deciqo/products", { signal: controller.signal })
      .then((data) => {
        if (!controller.signal.aborted) setProducts(data.products);
      })
      .catch((e: ApiError) => {
        if (!controller.signal.aborted) setError(e.code);
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [revision, summary]);
  return (
    <>
      <header className="page-header">
        <div>
          <h1>{t("catalog.title")}</h1>
          <p className="muted">{t("catalog.lead")}</p>
        </div>
        <Button
          busy={busy}
          disabled={loading || products.length === 0}
          onClick={() =>
            void run(
              () => request("/deciqo/analyse-all", { method: "POST" }),
              "catalog.done",
              "catalog.analysing",
            )
          }
        >
          {t("catalog.analyse")}
        </Button>
      </header>
      {loading ? (
        <LoadingState />
      ) : error ? (
        <Notice
          tone="alert"
          action={
            <Button variant="outline" onClick={() => setRevision((r) => r + 1)}>
              {t("common.retry")}
            </Button>
          }
        >
          {localizeError(error)}
        </Notice>
      ) : (
        <Card>
          {products.length === 0 ? (
            <EmptyState
              title={t("catalog.empty")}
              description={t("catalog.emptyHint")}
              action={
                <a className="btn btn--primary" href="#/app/sources">
                  {t("catalog.add")}
                </a>
              }
            />
          ) : (
            <Table>
              <thead>
                <tr>
                  {[
                    "name",
                    "channel",
                    "reviews",
                    "rating",
                    "findings",
                    "fixable",
                    "analysis",
                  ].map((key) => (
                    <th scope="col" key={key}>
                      {t("catalog." + key)}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {products.map((product) => (
                  <tr key={product.id}>
                    <td>
                      <a
                        href={
                          "#/app/listings/" + encodeURIComponent(product.id)
                        }
                      >
                        {product.title}
                      </a>
                      {product.synthetic && (
                        <div>
                          <Chip>{t("catalog.synthetic")}</Chip>
                        </div>
                      )}
                    </td>
                    <td>{product.channel}</td>
                    <td className="count">{product.reviews}</td>
                    <td className="count">
                      {product.rating == null
                        ? "—"
                        : new Intl.NumberFormat(language, {
                            maximumFractionDigits: 1,
                          }).format(product.rating)}
                    </td>
                    <td className="count">{product.findings}</td>
                    <td className="count">{product.fixable}</td>
                    <td>
                      <Chip
                        tone={
                          product.analysis_status === "failed"
                            ? "alert"
                            : product.stale
                              ? "warn"
                              : "muted"
                        }
                      >
                        {t(
                          "catalog." +
                            (product.stale
                              ? "stale"
                              : product.analysis_status === "ready"
                                ? "ready"
                                : product.analysis_status === "failed"
                                  ? "failed"
                                  : "pending"),
                        )}
                      </Chip>
                      {product.engine && (
                        <p className="muted">
                          {t(
                            "catalog." +
                              (product.engine === "ai" ? "ai" : "rules"),
                          )}
                        </p>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          )}
        </Card>
      )}
    </>
  );
}
