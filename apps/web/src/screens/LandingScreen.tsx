import "@/styles/landing.css";
import { useEffect } from "react";
import { FactGate } from "@/components/landing/FactGate";
import { Hero, SiteNav } from "@/components/landing/Hero";
import { useDemoStart } from "@/components/landing/hooks";
import { Bento, Channels, Close, Compare, Faq, Footer, Honest, Steps } from "@/components/landing/Sections";

/** Landing `#/`: satu isu nyata di hero, di mana alur kerja hari ini bocor, satu hal yang Deciqo
 *  tolak lakukan (fact gate), jalurnya, isinya, yang sudah dan belum terbukti, lalu akun demo. */
export default function LandingScreen() {
  const demo = useDemoStart();
  useEffect(() => {
    // Anchor seperti `#how` bukan rute; gulir ke bagiannya saat halaman dibuka langsung di sana.
    const hash = window.location.hash;
    if (hash && !hash.startsWith("#/")) {
      document.getElementById(hash.slice(1))?.scrollIntoView();
    }
  }, []);
  return (
    <div className="lp">
      <SiteNav demo={demo} />
      <main>
        <Hero demo={demo} />
        <Channels />
        <Compare />
        <FactGate />
        <Steps />
        <Bento />
        <Honest />
        <Faq />
        <Close demo={demo} />
      </main>
      <Footer />
    </div>
  );
}
