# DJ Mantra — ecstatic dance

Bilingual (HR / EN) one page bio for **Marko Boško / DJ Mantra**, written for the ecstatic dance community in Croatia.

Covers the percussion work and Tribal Jam Orchestra, the seven years in Auroville and the Sun Moon Yoga method, the lineage of teachers, and the three part arc of an evening, shown as three illustrated acts with his modules in each: I Opening (yoga and pranayama, guided meditation, vowel toning), II The dance (DJ set, live drums), III Closing (sound bath). Galleries of **Tribal Jam Orchestra** (Zagreb, since 2011) and **Tribal Jam Collective** (KalaBhumi Studio, Auroville) open in a lightbox.

## Technical notes

* One static `index.html`. No framework, no build step, no dependencies, no tracking.
* Bilingual dictionary compiled into the page. Croatian is the default, choice persisted in `localStorage` with a cookie fallback.
* Images are self hosted in `assets/` (`assets/tjo/`, `assets/tjc/`, `act-*.jpg`), lazy loaded below the fold.
* Headings in **Spectral** (Google Fonts), chosen 5.10.2026 because it draws č ć š ž đ properly; Cormorant Garamond drew a loose floating caron on ž and was dropped.
* A version label sits top left (`v3`), bumped on every change, so a cached copy is easy to tell from the current one.
* Responsive to 360px, `prefers-reduced-motion` respected.

## Deploy

Cloudflare Pages, project `djmantra`. The `main` branch is the source of truth.

## Contact

marko.bosko@gmail.com
