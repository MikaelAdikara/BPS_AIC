import { useEffect, useId, useRef, useState, type FormEvent } from "react";
import { useAuth } from "@/api/auth";
import { useWorkspace } from "@/api/workspace";
import { request, ApiError } from "@/api/http.js";
import { useI18n } from "@/lib/i18n";
import { LazadaFetch } from "@/components/LazadaFetch";
import { DemoReview } from "@/components/DemoReview";
import {
  ChannelBoard,
  SamplePackCard,
  type SamplePack,
} from "@/components/insight/ChannelBoard";
import { sortChannels } from "@/lib/insight-model";
import {
  Button,
  Card,
  Chip,
  EmptyState,
  Field,
  LoadingState,
  Notice,
} from "@/components/ui";
const options = {
  woocommerce: "WooCommerce",
  lazada: "Lazada",
  tokopedia: "Tokopedia",
  shopee: "Shopee",
  tiktok: "TikTok Shop",
  blibli: "Blibli",
  manual: "Manual",
};
type Sample = SamplePack;
export function SourcesScreen() {
  const { user, refresh: refreshAuth } = useAuth();
  const { channels, loading, error, refresh, run, busy } = useWorkspace();
  const { t, language, localizeError } = useI18n();
  const [selected, setSelected] = useState(user?.channels ?? []);
  const [editing, setEditing] = useState(!user?.channels?.length);
  const [tab, setTab] = useState(user?.channels?.[0] ?? "woocommerce");
  const [localError, setLocalError] = useState<string | null>(null);
  const [samples, setSamples] = useState<Sample[]>([]);
  const [sampleLoading, setSampleLoading] = useState(true);
  const [sampleError, setSampleError] = useState<string | null>(null);
  const [sampleRevision, setSampleRevision] = useState(0);
  const [mode, setMode] = useState("demo");
  const [url, setUrl] = useState("");
  const [key, setKey] = useState("");
  const [secret, setSecret] = useState("");
  const [title, setTitle] = useState("");
  const [productUrl, setProductUrl] = useState("");
  const [listing, setListing] = useState("");
  const [reviews, setReviews] = useState("");
  const [csv, setCsv] = useState("");
  const [filename, setFilename] = useState("");
  const [stats, setStats] = useState<Record<string, number> | null>(null);
  const [confirm, setConfirm] = useState<"reset" | "delete" | null>(null);
  const dialog = useRef<HTMLDialogElement>(null);
  const csvInput = useRef<HTMLInputElement>(null);
  const id = useId();
  const source = channels.find((channel) => channel.key === tab);
  useEffect(() => {
    const controller = new AbortController();
    setSampleLoading(true);
    setSampleError(null);
    request("/deciqo/samples", { signal: controller.signal })
      .then((data) => {
        if (!controller.signal.aborted) setSamples(data.samples);
      })
      .catch((e: ApiError) => {
        if (!controller.signal.aborted) setSampleError(e.code);
      })
      .finally(() => {
        if (!controller.signal.aborted) setSampleLoading(false);
      });
    return () => controller.abort();
  }, [sampleRevision]);
  useEffect(() => {
    if (confirm) dialog.current?.showModal();
    else dialog.current?.close();
  }, [confirm]);
  async function perform(
    task: () => Promise<unknown>,
    success: string,
    label?: string,
  ) {
    setLocalError(null);
    await run(
      async () => {
        try {
          return await task();
        } catch (e) {
          setLocalError((e as ApiError).code ?? "request_failed");
          throw e;
        }
      },
      success,
      label,
    );
  }
  async function saveChannels() {
    await perform(async () => {
      await request("/auth/me", {
        method: "PATCH",
        body: { channels: selected },
      });
      await refreshAuth(true);
      setEditing(false);
      if (!selected.includes(tab)) setTab(selected[0] ?? "woocommerce");
    }, "sources.saved");
  }
  async function connect(event: FormEvent) {
    event.preventDefault();
    await perform(async () => {
      const result = await request("/deciqo/woo/connect", {
        method: "POST",
        body: {
          mode,
          base_url: url,
          consumer_key: key,
          consumer_secret: secret,
        },
      });
      setKey("");
      setSecret("");
      return result;
    }, "sources.connected");
  }
  async function importReviews(event: FormEvent) {
    event.preventDefault();
    setStats(null);
    await perform(
      async () => {
        const result = await request("/deciqo/import", {
          method: "POST",
          body: {
            channel: tab,
            product_title: title,
            product_url: productUrl,
            listing,
            reviews_text: csv ? "" : reviews,
            csv_text: csv,
          },
        });
        setStats(result.stats);
        return result;
      },
      "sources.importedDone",
      "sources.importing",
    );
  }
  const date = (value: string) => new Date(value).toLocaleString(language);
  const shownSamples = samples.filter((sample) => sample.channel === tab);
  return (
    <>
      <header className="page-header">
        <div>
          <h1>{t("sources.title")}</h1>
          <p className="muted">{t("sources.lead")}</p>
        </div>
        <Button variant="outline" onClick={() => setEditing((value) => !value)}>
          {t("sources.choose")}
        </Button>
      </header>
      <div className="stack sources-page">
        {editing && (
          <Card title={t("sources.picker")}>
            <fieldset className="source-grid">
              <legend className="visually-hidden">{t("sources.picker")}</legend>
              {Object.entries(options).map(([channel, label]) => (
                <label key={channel} className="source-choice">
                  <input
                    type="checkbox"
                    checked={selected.includes(channel)}
                    onChange={(event) =>
                      setSelected((current) =>
                        event.target.checked
                          ? [...current, channel]
                          : current.filter((value) => value !== channel),
                      )
                    }
                  />
                  <span>
                    <strong>{label}</strong>
                    <span className="muted">
                      {" "}
                      ·{" "}
                      {t(
                        "sources." +
                          (channel === "woocommerce"
                            ? "connection"
                            : channel === "lazada"
                              ? "fetch"
                              : "imported"),
                      )}
                    </span>
                  </span>
                </label>
              ))}
            </fieldset>
            <Button
              busy={busy}
              disabled={!selected.length}
              onClick={() => void saveChannels()}
            >
              {t("sources.save")}
            </Button>
          </Card>
        )}
        {localError && (
          <Notice tone="alert">
            {localError === "file_too_large"
              ? t("sources.tooLarge")
              : localizeError(localError)}
          </Notice>
        )}
        {loading ? (
          <LoadingState />
        ) : error ? (
          <Notice
            tone="alert"
            action={
              <Button onClick={() => void refresh()}>
                {t("common.retry")}
              </Button>
            }
          >
            {localizeError(error)}
          </Notice>
        ) : (
          <>
            {!user?.channels?.length ? (
              <EmptyState title={t("sources.empty")} description={t("sources.picker")} />
            ) : (
              <>
                <ChannelBoard
                  keys={sortChannels([
                    ...new Set([
                      ...user.channels,
                      ...channels.filter((c) => c.products > 0).map((c) => c.key),
                    ]),
                  ])}
                  channels={channels}
                  active={tab}
                  onSelect={(channel) => {
                    setTab(channel);
                    setStats(null);
                    setLocalError(null);
                  }}
                />
                {source?.last_error && (
                  <Notice tone="warn">
                    <p>{t("sources.sourceError")}</p>
                  </Notice>
                )}
                {tab === "woocommerce" ? (
                  <Card title={t("sources.woo")} lead={t("sources.readonly")}>
                    <form
                      className="stack sources-form"
                      onSubmit={(event) => void connect(event)}
                    >
                      <div className="field">
                        <label htmlFor={id + "-mode"}>
                          {t("sources.mode")}
                        </label>
                        <select
                          id={id + "-mode"}
                          value={mode}
                          onChange={(event) => setMode(event.target.value)}
                        >
                          {["demo", "own", "server"].map((value) => (
                            <option key={value} value={value}>
                              {t("sources." + value)}
                            </option>
                          ))}
                        </select>
                      </div>
                      {mode === "own" && (
                        <>
                          <Field
                            label={t("sources.url")}
                            type="url"
                            required
                            value={url}
                            onChange={(event) => setUrl(event.target.value)}
                          />
                          <Field
                            label={t("sources.key")}
                            required
                            autoComplete="off"
                            value={key}
                            onChange={(event) => setKey(event.target.value)}
                          />
                          <Field
                            label={t("sources.secret")}
                            type="password"
                            required
                            autoComplete="off"
                            value={secret}
                            onChange={(event) => setSecret(event.target.value)}
                          />
                        </>
                      )}
                      <div className="finding-picker">
                        <Button type="submit" busy={busy}>
                          {t("sources.connect")}
                        </Button>
                        <Button
                          variant="outline"
                          busy={busy}
                          onClick={() =>
                            void perform(
                              () =>
                                request("/deciqo/woo/sync", { method: "POST" }),
                              "sources.synced",
                              "sources.syncing",
                            )
                          }
                        >
                          {t("sources.sync")}
                        </Button>
                        <Button
                          variant="text"
                          disabled={busy}
                          onClick={() =>
                            void perform(
                              () =>
                                request("/deciqo/woo/connect", {
                                  method: "DELETE",
                                }),
                              "sources.disconnected",
                            )
                          }
                        >
                          {t("sources.disconnect")}
                        </Button>
                      </div>
                    </form>
                  </Card>
                ) : (
                  <Card title={options[tab as keyof typeof options] ?? tab}>
                    <form
                      className="stack sources-form"
                      onSubmit={(event) => void importReviews(event)}
                    >
                      <Field
                        label={t("sources.product")}
                        required
                        maxLength={300}
                        value={title}
                        onChange={(event) => setTitle(event.target.value)}
                      />
                      <Field
                        label={t("sources.productUrl")}
                        type="url"
                        value={productUrl}
                        onChange={(event) => setProductUrl(event.target.value)}
                      />
                      <div className="field">
                        <label htmlFor={id + "-listing"}>
                          {t("sources.listing")}
                        </label>
                        <textarea
                          id={id + "-listing"}
                          maxLength={20000}
                          value={listing}
                          onChange={(event) => setListing(event.target.value)}
                        />
                        <p className="muted">{t("sources.listingHint")}</p>
                      </div>
                      <div className="field">
                        <label htmlFor={id + "-reviews"}>
                          {t("sources.reviews")}
                        </label>
                        <textarea
                          id={id + "-reviews"}
                          disabled={!!csv}
                          required={!csv}
                          maxLength={500000}
                          value={reviews}
                          onChange={(event) => setReviews(event.target.value)}
                        />
                        <p className="muted">{t("sources.reviewsHint")}</p>
                      </div>
                      <div className="field">
                        <label htmlFor={id + "-csv"}>{t("sources.csv")}</label>
                        <input
                          id={id + "-csv"}
                          type="file"
                          ref={csvInput}
                          accept=".csv,text/csv"
                          onChange={async (event) => {
                            const file = event.target.files?.[0];
                            if (!file) return;
                            if (file.size > 5 * 1024 * 1024) {
                              setLocalError("file_too_large");
                              event.target.value = "";
                              return;
                            }
                            try {
                              setCsv(await file.text());
                              setFilename(file.name);
                              setLocalError(null);
                            } catch {
                              setLocalError("invalid_response");
                            }
                          }}
                        />
                        <p className="muted">{t("sources.csvHint")}</p>
                        {filename && (
                          <>
                            <p className="break-word">
                              {t("sources.csvLoaded", { name: filename })}
                            </p>
                            <Button
                              variant="text"
                              onClick={() => {
                                setCsv("");
                                setFilename("");
                                if (csvInput.current) csvInput.current.value = "";
                              }}
                            >
                              {t("sources.clearFile")}
                            </Button>
                          </>
                        )}
                      </div>
                      <div>
                        <Button type="submit" busy={busy}>
                          {t("sources.import")}
                        </Button>
                      </div>
                    </form>
                    {stats && (
                      <Notice tone="good">
                        <div>
                          <p>{t("sources.stats", stats)}</p>
                          <a href="#/app/issues">{t("sources.issues")}</a>
                        </div>
                      </Notice>
                    )}
                  </Card>
                )}
                <Card title={t("sources.samples")} lead={t("sources.packsLead")}>
                  {sampleLoading ? (
                    <LoadingState />
                  ) : sampleError ? (
                    <Notice
                      tone="alert"
                      action={
                        <Button
                          onClick={() =>
                            setSampleRevision((value) => value + 1)
                          }
                        >
                          {t("common.retry")}
                        </Button>
                      }
                    >
                      {localizeError(sampleError)}
                    </Notice>
                  ) : shownSamples.length === 0 ? (
                    <p className="muted">{t("sources.sampleEmpty")}</p>
                  ) : (
                    <div className="pack-grid">
                      {shownSamples.map((sample) => (
                        <SamplePackCard
                          key={sample.name}
                          pack={sample}
                          busy={busy}
                          onLoad={() =>
                            void perform(
                              () =>
                                request(
                                  "/deciqo/samples/" +
                                    encodeURIComponent(sample.name),
                                  { method: "POST" },
                                ),
                              "sources.sampleDone",
                              "sources.importing",
                            )
                          }
                        />
                      ))}
                    </div>
                  )}
                </Card>
                {tab === "lazada" && <LazadaFetch />}
                {source?.synthetic && tab === "woocommerce" && (
                  <Card title={t("sources.demoTools")}>
                    <details>
                      <summary>{t("sources.demoTools")}</summary>
                      <p>{t("sources.liveHint")}</p>
                      <p className="muted">{t("sources.operational")}</p>
                      <DemoReview />
                      <Button
                        busy={busy}
                        onClick={() =>
                          void perform(
                            () =>
                              request("/deciqo/demo/live", { method: "POST" }),
                            "sources.liveDone",
                            "sources.syncing",
                          )
                        }
                      >
                        {t("sources.live")}
                      </Button>
                    </details>
                  </Card>
                )}
              </>
            )}
          </>
        )}
        <Card title={t("sources.workspace")}>
          <div className="finding-picker">
            <Button
              variant="outline"
              disabled={busy}
              onClick={() => setConfirm("reset")}
            >
              {t("sources.reset")}
            </Button>
            <Button
              variant="danger"
              disabled={busy}
              onClick={() => setConfirm("delete")}
            >
              {t("sources.delete")}
            </Button>
          </div>
        </Card>
      </div>
      <dialog
        ref={dialog}
        className="source-dialog"
        aria-labelledby={id + "-dialog"}
        onCancel={() => setConfirm(null)}
      >
        <h2 id={id + "-dialog"}>
          {t(
            "sources." +
              (confirm === "delete" ? "deleteTitle" : "confirmTitle"),
          )}
        </h2>
        <p>
          {t("sources." + (confirm === "delete" ? "deleteHint" : "resetHint"))}
        </p>
        <div className="finding-picker">
          <Button autoFocus variant="outline" onClick={() => setConfirm(null)}>
            {t("sources.cancel")}
          </Button>
          <Button
            variant="danger"
            onClick={() => {
              const action = confirm;
              setConfirm(null);
              if (action)
                void perform(
                  () =>
                    request(
                      action === "delete"
                        ? "/deciqo/workspace"
                        : "/deciqo/workspace/reset",
                      { method: action === "delete" ? "DELETE" : "POST" },
                    ),
                  action === "delete" ? "sources.deleted" : "sources.resetDone",
                );
            }}
          >
            {t("sources.confirm")}
          </Button>
        </div>
      </dialog>
    </>
  );
}
