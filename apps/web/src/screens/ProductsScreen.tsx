import { useEffect, useState } from "react";
import { request, ApiError } from "@/api/http.js";
import { useWorkspace } from "@/api/workspace";
import { ScanSearch, Star } from "lucide-react";
import { ProductImage } from "@/components/product/ProductImage";
import { useI18n } from "@/lib/i18n";
import { Meter } from "@/components/visual/charts";
import { RunPanel } from "@/components/RunPanel";
import { ChannelDot } from "@/components/insight/IssueMap";
import { channelLabel } from "@/lib/insight-model";
import {
  ListFilters,
  useListFilters,
  filterQuery,
} from "@/components/ListFilters";
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
  /** Belum dikirim GET /deciqo/products; dipakai bila tersedia. */
  image_url?: string | null;
}
export function ProductsScreen() {
  const { filters, setFilters, clear } = useListFilters(
    "deciqo-products-filters",
  );
  const params = filterQuery(filters);
  const { t, language, localizeError } = useI18n();
  const { summary, busy, run, status } = useWorkspace();
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [revision, setRevision] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setError(null);
    const timer = setTimeout(() => {
      request("/deciqo/products?" + params, { signal: controller.signal })
        .then((data) => {
          if (!controller.signal.aborted) setProducts(data.products);
        })
        .catch((e: ApiError) => {
          if (!controller.signal.aborted) setError(e.code);
        })
        .finally(() => {
          if (!controller.signal.aborted) setLoading(false);
        });
    }, 200);
    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [revision, summary, params]);
  return (
    <>
      <header className="page-header">
        <div>
          <h1>{t("catalog.title")}</h1>
          <p className="muted">{t("catalog.lead")}</p>
        </div>
        <Button
          busy={busy}
          disabled={!status?.engine_ready || !summary?.products}
          onClick={() =>
            void run(
              () => request("/deciqo/analyse-all", { method: "POST" }),
              "catalog.done",
              "catalog.analysing",
            )
          }
        >
          <ScanSearch size={16} aria-hidden />
          {t("catalog.analyse")}
        </Button>
      </header>
      <RunPanel />
      <div className="toolbar-card">
        <ListFilters
          filters={filters}
          onChange={setFilters}
          onClear={clear}
          products
        />
      </div>
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
              title={t(filters.q || filters.channel || filters.status ? "filters.noMatches" : "catalog.empty")}
              description={t(filters.q || filters.channel || filters.status ? "filters.hint" : "catalog.emptyHint")}
              action={
                filters.q || filters.channel || filters.status ? <Button onClick={clear}>{t("filters.clear")}</Button> : <a className="btn btn--primary" href="#/app/sources">
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
                      <div className="product-cell">
                        <ProductImage
                          src={product.image_url}
                          size={40}
                          className="product-cell__thumb"
                        />
                        <div>
                          <a
                            className="product-cell__link"
                            title={product.title}
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
                        </div>
                      </div>
                    </td>
                    <td>
                      <span className="channel-tag">
                        <ChannelDot channel={product.channel} />
                        {channelLabel(product.channel)}
                      </span>
                    </td>
                    <td className="count">{product.reviews}</td>
                    <td className="rating-cell">
                      {product.rating == null ? (
                        "—"
                      ) : (
                        <>
                          <span className="count">
                            <Star size={13} className="star-icon" aria-hidden />
                            {new Intl.NumberFormat(language, {
                              maximumFractionDigits: 1,
                            }).format(product.rating)}
                          </span>
                          <Meter
                            value={product.rating}
                            max={5}
                            label={t("catalog.rating")}
                            tone={product.rating < 3 ? "alert" : product.rating < 4 ? "warn" : "good"}
                          />
                        </>
                      )}
                    </td>
                    <td>
                      <span className={"num-badge" + (product.findings ? " is-on" : "")}>
                        {product.findings}
                      </span>
                    </td>
                    <td>
                      <span className={"num-badge" + (product.fixable ? " is-fix" : "")}>
                        {product.fixable}
                      </span>
                    </td>
                    <td>
                      <Chip
                        tone={
                          product.analysis_status === "failed"
                            ? "alert"
                            : product.stale
                              ? "warn"
                              : product.analysis_status === "ready"
                                ? "good"
                                : "muted"
                        }
                      >
                        <i className="status-dot" aria-hidden />
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
