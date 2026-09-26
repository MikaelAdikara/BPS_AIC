import type { Issue } from "./workspace";
export interface Evidence {
  review_id: string;
  quote: string;
  rating?: number | null;
  review_time?: string | null;
  variant?: string;
}
export interface DraftSection {
  finding_id: string;
  status: string;
  text: string;
  rendered_from: string | null;
  reasons: string[];
}
export interface Finding extends Issue {
  listing_fixable: boolean;
  state: string;
  buyer_expectation: string;
  merchant_question: string;
  fact: {
    value: string;
    unit: string;
    variant: string;
    confirmed_at: string;
  } | null;
  draft_status: string | null;
  metrics: {
    support: number;
    denominator: number;
    candidates_read: number;
    support_is_minimum: boolean;
    share: number;
    contradicting: number;
    hidden_high_star: number;
    with_photos: number;
    rating_now?: number | null;
    rating_without?: number | null;
    variants?: {variant: string; complaints: number; complaint_share: number; review_share: number; exploratory: boolean}[];
  };
  evidence: Evidence[];
  contradicting: Evidence[];
  rejected: { review_id: string; reason: string }[];
  uncertain: number;
  listing_check: {
    status: string;
    quote: string;
    related: string[];
    coverage?: {
      chars_checked: number;
      chars_total: number;
      model_chars?: number;
      images_read: number;
      images_total: number;
    };
  };
  follow_up: {
    state: string;
    acted_at: string;
    after: number;
    complaints: number;
    undated: number;
  } | null;
}
export interface ProductView {
  product: {
    id: string;
    title: string;
    channel: string;
    url: string;
    listing_text: string;
    listing_edit_text?: string;
    listing_provided: boolean;
    data_origin: string;
    captured_at: string;
    synthetic: boolean;
    image_url?: string | null;
  };
  source: { status: string; last_success_at: string | null };
  stats: {
    reviews: number;
    rating: number | null;
    rating_hist: Record<string, number>;
    with_photos: number;
  };
  analysis: {
    engine: string;
    status: string;
    created_at: string;
    trace: Record<string, string | number>[];
  } | null;
  findings: Finding[];
  not_detected: { id: string; attribute_local: string }[];
  draft: { status: string; sections: DraftSection[] } | null;
  generic_draft: {
    model: string;
    same_bundle: boolean;
    gate_version: string;
    problems: { problem: string; suggestion: string }[];
    sentences: { text: string; status: string; reasons: string[]; unsupported: string[] }[];
    counts: { sentences: number; blocked: number };
  } | null;
  decisions: {
    finding_id: string;
    decision: string;
    note?: string;
    reason?: string;
    created_at: string;
  }[];
}
