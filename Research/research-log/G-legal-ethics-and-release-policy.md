# G — Legal, ethical and community considerations for a public ad-annotation/ad-skip tool
Accessed: 2026-09-01

## Status
COMPLETE — 2026-09-02. 75 sources (fetched: S1–S9, S36–S49, S51–S56, S58–S75; snippet-only: S10–S35; failed: S50, S57 and two others logged under 'Failed fetches'). WebSearch budget was exhausted session-wide mid-run; all later work used WebFetch of primary URLs and local pdftotext extraction.

## Sources

### S1. Fox Broadcasting Co. v. Dish Network L.L.C., 723 F.3d 1067 (9th Cir. July 24, 2013), No. 12-57048 — https://cdn.ca9.uscourts.gov/datastore/opinions/2013/07/24/12-57048.pdf
- Type: legal
- Verified: fetched (PDF saved locally; text extracted with pdftotext; quotes verbatim)
- Key facts:
  - Facts found: "By default, AutoHop is not selected." "AutoHop does not delete commercials from the recording." Dish technicians "manually view Fox's primetime programing each night and technologically mark the beginning and end of each commercial." "The program content is not altered in any way."
  - Marks are sent to subscribers in a separate "announcement" file (i.e., side-car metadata, not edited video). Dish also made "quality assurance" copies to check marks — the only copies the district court found likely infringing/breaching contract.
  - Direct infringement: Dish's "program creates the copy only in response to the user's command" (volitional-conduct reasoning, citing Cartoon Network).
  - Secondary liability fails because customers' recording is Sony fair use; Sony noted "about 25 percent of Betamax users fast-forwarded through commercials" (464 U.S. at 452 n.36) but "never expressly decided whether commercial-skipping and library-building were fair uses."
  - Holding on ad-skipping: "commercial-skipping does not implicate Fox's copyright interest because Fox owns the copyrights to the television programs, not to the ads." "If recording an entire copyrighted program is a fair use, the fact that viewers do not watch the ads ... cannot transform the recording into a copyright violation." "any analysis of the market harm should exclude consideration of AutoHop."
  - The market harm Fox alleged "results from the automatic commercial-skipping, not the recording"; "AutoHop, standing alone, does not infringe."
  - Procedural posture: review of a preliminary-injunction denial (abuse of discretion), not a final merits judgment.
- Relevance to AdVTT:
  - Strongest US authority that end-user ad-skipping of a lawfully held recording is not a copyright injury to the programme owner; also that a *separate announcement/marker file* leaving the programme "not altered in any way" was the design the court described approvingly. AdVTT's side-car VTT is the same architecture.
  - The only exposure in the case was copies Dish made *for itself*; a tool running on the user's machine on the user's copy has no analogue.
  - Podcast wrinkle (analysis, not advice): for baked-in host-read ads the podcaster typically owns the copyright in the ad read, so the "Fox doesn't own the ads" limb is weaker; the Sony fair-use limb (the user's copy is lawful; not watching part of it is not infringement) still stands.

### S2. SponsorBlock — Database and API License (GitHub wiki) — https://github.com/ajayyy/SponsorBlock/wiki/Database-and-API-License
- Type: repo / policy
- Verified: fetched
- Key facts:
  - "The API and database follow CC BY-NC-SA 4.0 unless you have explicit permission."
  - "If you need to use the database or API in a way that violates this license, contact me ... I may grant you access under a different license."
  - Attribution template supplied; full database dump downloadable at https://sponsor.ajay.app/database.
  - Code licence not stated on this page (README check pending; commonly reported as LGPL-3.0 — unverified).
- Relevance to AdVTT:
  - The most-used crowd ad-segment project publishes its *labels* openly under a non-commercial share-alike licence and treats them as its own database, not as a derivative of YouTube's videos.
  - Template for any future AdVTT label set: CC BY-NC-SA (or CC0/ODbL if downstream commercial reuse is wanted).

### S3. Adblock Radio — "Adblock Radio is a perceptual ad blocker" (blog, 2019-10-25) — https://www.adblockradio.com/blog/2019/10/25/adblock-radio-is-a-perceptual-ad-blocker/index.html
- Type: blog
- Verified: fetched
- Key facts:
  - Author's framing: "Ad blockers are not a solution, they are merely a counter power for users that are tired of ads."
  - Predicts media will move to subscription or product placement; states the goal is sustainable funding, not ad-blocking per se.
  - Project "crowdsources a database of ads"; page does not say whether the tool auto-skips or only signals; licence not stated here (repo fetch pending).
- Relevance to AdVTT:
  - Precedent for an audio-domain ad detector released openly with an explicit ethical framing ("counter power", not "solution").
  - Adblock Radio's classifier is acoustic (ads/talk/music); AdVTT's transcript+LLM approach is the natural successor for host-read ads.

### S4. W3C TDM Reservation Protocol (TDMRep), Final Community Group Report, 2024-05-10 — https://www.w3.org/community/reports/tdmrep/CG-FINAL-tdmrep-20240510/
- Type: spec
- Verified: fetched
- Key facts:
  - Status: "Final Community Group Report", not a W3C Standard.
  - Three mechanisms: HTTP response header `tdm-reservation` (+ optional `tdm-policy` URL); `/.well-known/tdmrep.json`; HTML `<meta name="tdm-reservation">`.
  - Values: 1 = "TDM rights are reserved"; 0 = "TDM rights are not reserved. TDM agents can mine the content".
  - Scope: "lawfully accessible Web content" generally; the HTTP-header and well-known variants apply to any HTTP-served resource, including audio enclosures.
- Relevance to AdVTT:
  - A ready-made, EU-law-anchored opt-out signal AdVTT can honour: check `tdm-reservation` on the enclosure URL / host before transcribing.
  - Cheap (one HEAD request or one well-known fetch per host) and gives podcasters a recognised lever without inventing a new RSS tag.

### S5. EFF — FAQ on ReplayTV owners' legal challenge, Newmark et al. v. Turner Broadcasting — https://www.eff.org/pages/faq-replaytv-owners-legal-challenge-newmark-et-al-
- Type: legal (advocacy summary)
- Verified: fetched
- Key facts:
  - 28 studios/networks sued ReplayTV/SONICblue in Oct 2001; five ReplayTV owners then sued for a declaration that time-shifting, commercial skipping and "Send Show" were "lawful under copyright law".
  - Studios' theory: devices enabling digital recording, commercial skipping and sharing = "contributory and vicarious copyright infringement".
  - Page is a snapshot; outcome not on it (see S10).
- Relevance to AdVTT:
  - Litigation risk historically fell on the *vendor shipping* the feature, not on users; the users' own declaratory claim was never decided on the merits.

### S6. The Brand Protection Blog — "German Federal Court refers ad blocker case back to Hamburg Higher Regional Court" (Aug 2025) — https://www.thebrandprotectionblog.com/2025/08/german-federal-court-refers-ad-blocker-case-back-to-hamburg-higher-regional-court/
- Type: legal (law-firm blog)
- Verified: fetched (thin excerpt)
- Key facts:
  - BGH I ZR 131/23, decided 31 July 2025; remanded to OLG Hamburg.
  - Dispute centres on "browser-generated data structures – specifically DOM and CSSOM trees" and whether altering them adapts a protected computer program (§ 69c UrhG).
- Relevance to AdVTT:
  - The live German theory is *modification of a copyrighted program in memory*. AdVTT emits a separate metadata file and alters neither the audio nor any program — structurally outside this theory (analysis, not advice).

### S7. Podnews — "EXCLUSIVE: Spotify threatens podcasting with ad-skipping tool" (2026-08-04) — https://podnews.net/update/spotify-skip-ahead
- Type: trade press
- Verified: fetched
- Key facts:
  - Spotify testing a "Skip ahead" button inside podcast ads and sponsorship messages; it also appears on creators' Patreon-style premium-subscription asks.
  - Podnews calls it "a significant threat to podcasting"; Spotify sells its own unskippable ads while enabling skipping of others'.
- Relevance to AdVTT:
  - The industry's loudest current objection is aimed at a *platform* doing it to creators' content without consent; the grievance is asymmetry and consent, not the listener's right to skip.
  - AdVTT should visibly exclude value-for-value / membership asks from default skip — exactly the element Podnews flagged as most egregious.

### S8. Hacker News — "The killer feature for using AI on podcasts is automatic ad blocking" (2024-08-12) — https://news.ycombinator.com/item?id=41221405
- Type: forum
- Verified: fetched
- Key facts:
  - Supportive: hands-free skipping while driving/exercising; SponsorBlock "saved me hours" on YouTube-hosted podcasts.
  - Nuance: "ad blocking on podcast doesn't cost the creators anything ... ad revenue is largely based on the number of downloads"; host-read ads are hard to separate cleanly.
  - Tools named: SponsorBlock, Podly Pure Podcasts (open-source), AdBlockPodcast.com (approx. $5/month).
- Relevance to AdVTT:
  - Open-source precedents that *cut* audio already exist (Podly); AdVTT's annotate-only posture is a differentiator.
  - Download-based measurement argument recurs in the community; see S30, S33.

### S9. Wikipedia — Cartoon Network, LP v. CSC Holdings, Inc., 536 F.3d 121 (2d Cir. Aug 4, 2008) — https://en.wikipedia.org/wiki/Cartoon_Network,_LP_v._CSC_Holdings,_Inc.
- Type: legal (secondary summary)
- Verified: fetched (opinion itself not fetched)
- Key facts:
  - Buffer copies of 0.1–1.2 s are not "fixed" for "more than a transitory duration".
  - Volitional conduct: Cablevision's role not "sufficiently proximate"; the customer who presses record makes the copy (following Netcom).
  - Per-subscriber transmissions are not "to the public"; cert. denied 2009; Aereo (2014) distinguished it.
- Relevance to AdVTT:
  - Supports the view that a tool producing copies only at the user's command places the copying on the user, whose time-shifting is Sony fair use.
  - A transcript is a *fixed* derived text, unlike a transitory buffer; fair use / TDM exceptions (S16–S21) are what cover it.

### S10. Paramount Pictures v. ReplayTV / SONICblue — SEC Form 8-K (2002-03-21) — https://www.sec.gov/Archives/edgar/data/850519/000089161802001354/f80095e8-k.htm ; EFF archive https://w2.eff.org/IP/Video/Paramount_v_ReplayTV/ ; summary https://project-disco.org/intellectual-property/100813-15-technologies-that-content-industries-sued-after-diamond-rio/
- Type: legal
- Verified: snippet-only
- Key facts:
  - Four suits filed Oct–Nov 2001 by 28 companies over ReplayTV 4000's Commercial Advance and Send Show.
  - SONICblue filed for bankruptcy March 2003; ReplayTV assets sold 25 April 2003 to Digital Networks North America; plaintiffs then stipulated to voluntary dismissal without prejudice; covenants not to sue given to the five Newmark plaintiffs.
  - No court ruled on whether Commercial Advance infringed.
- Relevance to AdVTT:
  - The only US case squarely about *automatic* ad-skipping shipped as a product ended in bankruptcy, not a ruling; the deterrent was litigation cost.
  - A solo maintainer's exposure is asymmetric in the same way; posture and framing matter as much as merits.

### S11. Fox Broadcasting Co. v. Dish Network, 747 F.3d 1060 (9th Cir., amended Jan 24, 2014), No. 13-56818 — https://www.loeb.com/en/insights/publications/2014/02/fox-broadcasting-co-v-dish-network-llc ; https://www.casemine.com/judgement/us/5914e0dcadd7b049348de177 ; C.D. Cal. 2015 summary https://www.copyright.gov/fair-use/summaries/fox-dish-cdcal2015.pdf
- Type: legal
- Verified: snippet-only
- Key facts:
  - Second appeal (Hopper Transfers / Dish Anywhere): denial of preliminary injunction affirmed; no likelihood of success on infringement or contract claims; no irreparable harm.
  - District court on remand (Jan 2015) granted Dish summary judgment on most copyright claims (snippet-level).
- Relevance to AdVTT:
  - Reinforces S1; courts declined to enjoin AutoHop over four years.

### S12. Fox–Dish settlement, Feb 2016 — https://www.hollywoodreporter.com/thr-esq/deal-fox-dish-agrees-disable-864208 ; https://variety.com/2016/biz/news/fox-broadcasting-dish-network-autohop-1201703348/
- Type: trade press
- Verified: snippet-only
- Key facts:
  - Joint statement: "AutoHop commercial-skipping functionality will not be available for owned and affiliated Fox stations until seven days after a program first airs."
- Relevance to AdVTT:
  - The commercial compromise was a *time window*, not abolition — a possible optional policy (no skip for the first N days after publication if a publisher signals it).

### S13. BGH, Urteil vom 19.04.2018 – I ZR 154/16 "Werbeblocker II" — https://dejure.org/dienste/vernetzung/rechtsprechung?Gericht=BGH&Datum=19.04.2018&Aktenzeichen=I+ZR+154/16 ; summary https://www.wettbewerbszentrale.de/bgh-sieht-adblock-plus-als-zulaessig-an/
- Type: legal
- Verified: snippet-only (fetch pending)
- Key facts:
  - Offering Adblock Plus is neither unlawful targeted obstruction (§ 4 Nr. 4 UWG) nor an aggressive practice; Axel Springer's claim dismissed.
  - Reasoning (summary): the user decides; publishers have no claim that users view ads and may deploy countermeasures (e.g., exclude ad-block users).
- Relevance to AdVTT:
  - Under German unfair-competition law, *shipping* a user-controlled blocker was lawful; decisive were user autonomy and publishers' ability to respond — both present for a local, opt-in annotator.

### S14. BGH, Urteil vom 31.07.2025 – I ZR 131/23 (Adblock Plus, copyright) — https://dejure.org/dienste/vernetzung/rechtsprechung?Gericht=BGH&Datum=31.07.2025&Aktenzeichen=I+ZR+131/23 ; https://www.heise.de/en/news/Copyright-Springer-vs-Adblock-Plus-enters-another-round-10505898.html ; https://medien.epd.de/article/3401
- Type: legal
- Verified: snippet-only (heise fetch pending)
- Key facts:
  - BGH held that on the OLG Hamburg's findings an infringement of computer-program copyright "cannot be denied" and remanded; it did *not* hold ad blockers infringe.
  - Open: whether the HTML/DOM/CSSOM in the browser is (a copy of) a protected program and whether suppression is an adaptation ("Umarbeitung").
  - Post-remand OLG Hamburg status as of 2026-09: NOT CHECKED (search budget exhausted) — gap.
- Relevance to AdVTT:
  - Even the most aggressive live theory targets *runtime modification of a program*; a side-car VTT/JSON does not modify anything (analysis, not advice).

### S15. YouTube ToS enforcement against ad blockers — https://www.ghacks.net/2025/03/18/google-pushing-ad-blockers-violate-youtubes-terms-of-service-banners-on-youtube/ ; YouTube Terms https://www.youtube.com/t/terms
- Type: policy / trade press
- Verified: snippet-only (ToS fetch pending)
- Key facts:
  - YouTube's position: "use of ad blockers" violates its ToS; on 15 April 2024 it announced stronger enforcement against third-party ad-blocking apps.
  - SponsorBlock skips *sponsor segments inside creator videos*, not YouTube's inserted ads; no legal action against SponsorBlock was found.
- Relevance to AdVTT:
  - Platform ToS, not copyright, is the lever platforms use; RSS podcasts have no gatekeeper ToS at playback time (S22–S24).
  - SponsorBlock's 5+ years without takedown is a meaningful precedent for *segment metadata* about third-party media.

### S16. Bartz v. Anthropic (N.D. Cal., Alsup J., order June 23, 2025; settlement Sept 2025) — https://www.akingump.com/en/insights/ai-law-and-regulation-tracker/district-court-rules-ai-training-can-be-fair-use-in-bartz-v-anthropic ; https://www.insidetechlaw.com/blog/2025/09/bartz-v-anthropic-settlement-reached-after-landmark-summary-judgment-and-class-certification
- Type: legal (law-firm summaries)
- Verified: snippet-only
- Key facts:
  - Training on lawfully acquired books "exceedingly transformative" → fair use; destructive scanning of purchased print books to searchable digital copies → fair use.
  - Acquiring/keeping pirated copies for a central library → not fair use; case then settled (figure reported approx. $1.5bn; unverified).
- Relevance to AdVTT:
  - *Source lawfulness* matters more than the analysis: run AdVTT on episodes the user lawfully obtained (open RSS enclosures), not on ripped platform-exclusive audio.
  - Format-shifting a lawfully held copy for searchability (audio → text) has direct support here and in S18.

### S17. Kadrey v. Meta (N.D. Cal., Chhabria J., June 25, 2025) — https://www.akingump.com/en/insights/ai-law-and-regulation-tracker/second-district-court-rules-ai-training-can-be-fair-use ; docket https://law.justia.com/cases/federal/district-courts/california/candce/3:2023cv03417/415175/598/
- Type: legal (summaries)
- Verified: snippet-only
- Key facts:
  - Summary judgment for Meta because plaintiffs' market-harm evidence was "so weak that it does not move the needle"; court stressed a better "market dilution" record could win elsewhere.
- Relevance to AdVTT:
  - Market harm is the fulcrum. AdVTT's output does not substitute for the episode; the harm podcasters would raise is *lost ad impressions*, which S1 holds is not a copyright interest of the programme owner.

### S18. Authors Guild v. HathiTrust, 755 F.3d 87 (2d Cir. 2014) and Authors Guild v. Google, 804 F.3d 202 (2d Cir. 2015) — https://www.copyright.gov/fair-use/summaries/authorsguild-hathitrust-2dcir2014.pdf ; https://www.copyright.gov/fair-use/summaries/authorsguild-google-2dcir2015.pdf
- Type: legal
- Verified: snippet-only (fetch pending)
- Key facts:
  - Full-text search is "quintessentially transformative"; "different in purpose, character, expression, meaning, and message" from the book.
  - Google Books: snippets provide "information about" the works rather than a substitute; display limits (snippet size, blacklisted pages) supported fair use.
- Relevance to AdVTT:
  - Analogy for machine transcription used to *classify* (not republish) and for short evidence quotes: information about the work, tightly bounded.
  - Keep evidence quotes short; never emit the full transcript in shared artefacts.

### S19. Feist Publications v. Rural Telephone, 499 U.S. 340 (1991) — https://www.bitlaw.com/source/cases/copyright/feist.html
- Type: legal
- Verified: snippet-only
- Key facts:
  - Facts are not copyrightable; compilation copyright is "thin" and covers only original selection/arrangement, never the facts.
- Relevance to AdVTT:
  - "Ad from 12:03.2 to 13:47.9, sponsor Acme" is a fact about the episode. Distributing timestamps/labels is not distributing the podcaster's expression (US analysis; the EU sui generis database right is a separate question about the *collector's* rights, not the podcaster's).

### S20. EU Directive 2019/790 (DSM), Arts. 3–4 TDM exceptions — https://legalblogs.wolterskluwer.com/copyright-blog/the-new-copyright-directive-text-and-data-mining-articles-3-and-4/ ; https://academic.oup.com/jiplp/article/19/5/453/7614898 ; EUR-Lex https://eur-lex.europa.eu/eli/dir/2019/790/oj (fetch pending)
- Type: legal
- Verified: snippet-only
- Key facts:
  - Art. 3: research organisations / heritage institutions, scientific research, no opt-out. Art. 4: anyone, any purpose, but rightsholders may reserve rights "in an appropriate manner, such as machine-readable means" (Art. 4(3)); lawful access required; copies kept only as long as necessary.
- Relevance to AdVTT:
  - Personal transcription of a lawfully accessed podcast for classification fits Art. 4 unless the podcaster reserved rights machine-readably (S4 TDMRep). Honouring `tdm-reservation` is therefore more than courtesy in the EU.

### S21. Non-EU TDM exceptions: UK CDPA s.29A — https://www.legislation.gov.uk/ukpga/1988/48/section/29A ; Japan Copyright Act Art. 30-4 — https://www.japaneselawtranslation.go.jp/en/laws/view/3379 ; Singapore Copyright Act 2021 ss.243–244 — https://sso.agc.gov.sg/Act/CA2021?ProvIds=P15-P28-
- Type: legal
- Verified: snippet-only (statute fetches pending)
- Key facts:
  - UK s.29A: copies for computational analysis only with lawful access and "for the sole purpose of research for a non-commercial purpose"; the copy may not be transferred or used otherwise; contract cannot override.
  - Japan Art. 30-4: uses "not intended to appreciate or enjoy" the expression (incl. information analysis) permitted unless they "unreasonably prejudice" the owner; any purpose.
  - Singapore s.244: "computational data analysis" for any purpose with lawful access and no supply of the copy to others (except for verification).
- Relevance to AdVTT:
  - UK is narrowest (non-commercial *research* only); a UK hobbyist transcribing for personal use is arguably outside it — genuine gap.
  - All three condition the exception on *not redistributing the copy*: transcripts must stay local; timestamps/labels are not copies.

### S22. Apple — Podcasts Connect ToS (Podnews diffs 2024/2026) — https://podnews.net/article/apple-podcast-connect-tos-24 ; https://podnews.net/article/apple-podcast-connect-tos-26 ; Apple Media Services Terms — https://www.apple.com/legal/internet-services/itunes/us/terms.html
- Type: policy
- Verified: snippet-only (fetch pending)
- Key facts:
  - Apple takes a licence to "create transcripts" and "generate chapters" from podcasts, with a creator opt-out from public display.
  - Media Services Terms: content "may only be used for personal, noncommercial purposes".
  - Apple Podcasts plays open RSS enclosures; Apple's terms govern its app/store, not the third-party MP3 fetched directly.
- Relevance to AdVTT:
  - The largest podcast platform machine-transcribes every show and publishes the text — normalising transcription as an ordinary derived artefact.
  - Ingest from the RSS enclosure, not via Apple/Spotify apps, to stay outside any app ToS.

### S23. Spotify / Megaphone terms — Podnews https://podnews.net/article/spotify-unskippable-ads-and-auto-skips ; https://podnews.net/update/spotify-unskippable-or-not ; Megaphone legal https://megaphone.spotify.com/legal ; Spotify for Creators Ads Terms https://support.spotify.com/us/creators/article/ads-terms/
- Type: policy / trade press
- Verified: snippet-only (fetches pending)
- Key facts:
  - Podnews reports Spotify's creator terms grant it "the right to transcribe" content and to strip/replace ads in hosted shows; Spotify's terms give it "the legal right to automatically skip everyone else's" ads.
  - Megaphone inserts ads at download time (server-side), so the ad is inside the file the listener receives.
  - No listener-facing clause prohibiting transcription or skipping of RSS-delivered audio surfaced.
- Relevance to AdVTT:
  - Platforms reserve for themselves exactly the powers (transcribe, strip ads) a listener tool exercises locally.
  - DAI ads are baked into the delivered MP3 — AdVTT must classify by content; container gives no signal.

### S24. Acast+ Terms & Conditions — https://www.acast.com/en/legal/terms-and-conditions-acast-plus ; Art19 terms https://art19.com/terms (fetch pending)
- Type: policy
- Verified: snippet-only
- Key facts:
  - Acast+ (paid ad-free/bonus feeds) prohibits reproducing, modifying, distributing or preparing derivative works of "the Acast+ Service".
  - Art19 listener-facing restrictions: NOT FOUND in snippets.
- Relevance to AdVTT:
  - Paid/private feeds carry contractual terms; document that users are responsible for their feed's terms and default to open public RSS.

### S25. youtube-dl RIAA DMCA takedown and reinstatement (Oct–Nov 2020) — https://www.eff.org/deeplinks/2020/11/github-reinstates-youtube-dl-after-riaas-abuse-dmca ; https://github.com/github/dmca/blob/master/2020/10/2020-10-23-RIAA.md
- Type: legal / repo
- Verified: snippet-only
- Key facts:
  - RIAA's §1201 theory failed: youtube-dl does not "circumvent" a technical protection measure; unit-test references to copyrighted songs were fair use; GitHub reinstated and created a $1M developer defence fund.
- Relevance to AdVTT:
  - Test fixtures naming real works drew fire even for a downloader; AdVTT fixtures containing *full transcripts* of real episodes are a larger target — keep them out of the public repo.

### S26. Podcasting 2.0 Value4Value — https://blog.podcastindex.org/html/AnotherWay-lJmNWj9T490hdmPmz5M4GV1Tlw6rDF.html ; https://podnews.net/article/boost ; namespace https://github.com/Podcastindex-org/podcast-namespace
- Type: spec / blog
- Verified: snippet-only
- Key facts:
  - `podcast:value` enables Lightning micropayments (streaming sats, boosts, boostagrams) as a "direct support model ... rather than traditional advertising".
  - Podcast Index API used by approx. 58 apps (snippet).
- Relevance to AdVTT:
  - The ecosystem's own no-ads alternative; AdVTT can surface `podcast:value`/`podcast:funding` in output so a player can offer "support this show" when a user skips.
  - Value-for-value asks inside audio should be classed as house/PROMOTION and excluded from default skip.

### S27. Podcasting 2.0 `podcast:txt` and the AI-disclosure debate — https://rss.com/blog/ai-disclosure-in-podcasting-what-it-is-why-it-matters-and-how-to-do-it/ ; https://podcasting2.org/docs/podcast-namespace
- Type: spec / blog
- Verified: snippet-only
- Key facts:
  - Four AI-disclosure proposals debated over approx. 18 months; current practice uses the generic `podcast:txt` container.
  - No dedicated "no-AI / no-transcription" or "ad-ranges" tag exists (coordinator notes namespace issue #254 rejected an ad-range tag "because this can be abused by ad blockers" — fetch pending).
- Relevance to AdVTT:
  - No podcaster-side opt-out tag exists today; `podcast:txt purpose="..."` is the least-friction vehicle if one is proposed; TDMRep (S4) is the existing web-standard fallback.

### S28. Jellyfin Intro Skipper plugin — https://github.com/intro-skipper/intro-skipper
- Type: repo
- Verified: snippet-only (fetch pending)
- Key facts:
  - Detects intros/credits by audio fingerprinting of the user's own files; "doesn't use any external databases".
  - Disclaimer: fingerprints "derived entirely from your own local media files"; sharing detection data "may violate the licenses, terms of service, or other agreements governing the underlying media".
- Relevance to AdVTT:
  - A mature skip tool that deliberately stays *local-only* and warns against sharing derived data — a reusable posture and disclaimer template.

### S29. AI/TDM opt-out mechanisms compared — IPTC https://iptc.org/std/guidelines/data-mining-opt-out/IPTC-Generative-AI-Opt-Out-Best-Practices.pdf ; Open Future https://openfuture.eu/wp-content/uploads/2023/09/Best-_practices_for_optout_ML_training.pdf ; EFF https://www.eff.org/deeplinks/2023/12/no-robotstxt-how-ask-chatgpt-and-google-bard-not-use-your-website-training ; C2PA statement 22 Jan 2026 (snippet)
- Type: spec / policy
- Verified: snippet-only
- Key facts:
  - Location-based (robots.txt, ai.txt, TDMRep) vs asset-based (IPTC, C2PA) vs registry (Spawning "Do Not Train"); beyond robots.txt "none of these has been widely adopted".
  - C2PA "confirmed on 22 January 2026" that Content Credentials are provenance and "do not themselves carry a do-not-train assertion".
- Relevance to AdVTT:
  - Honour the cheapest widely understood signals (robots.txt-style disallow on the enclosure host, TDMRep); don't invent a bespoke one first.

### S30. IAB Tech Lab Podcast Technical Measurement Guidelines v2.3 (public comment, July 2026) — https://iabtechlab.com/wp-content/uploads/2026/07/PubComment-PodcastMeasurement_v2.3.pdf
- Type: spec
- Verified: snippet-only
- Key facts:
  - Measurement is download/IP-UA based; guidelines address de-duplication "where the podcast consumer might be skipping ahead". No IAB statement on podcast ad-blocking found.
- Relevance to AdVTT:
  - Skipping does not reduce the counted impression under current measurement; the harm is to *advertiser effectiveness*, not to reported numbers — until measurement changes.

### S31. Open-source licence share — OSI 2023 https://opensource.org/blog/the-most-popular-licenses-for-each-language-2023 ; linuxiac 2025 https://linuxiac.com/mit-and-apache-2-0-lead-open-source-licensing-in-2025/ ; RedMonk 2026 https://redmonk.com/sogrady/2026/03/25/open-source-licensing-2026/
- Type: blog / dataset
- Verified: snippet-only
- Key facts:
  - PyPI 2023: MIT 29.14%, Apache-2.0 23.98% (OSI).
  - 2025: MIT remains most viewed licence (approx. 1.53M pageviews vs Apache-2.0 approx. 344k).
- Relevance to AdVTT:
  - Python norm is permissive; MIT or Apache-2.0 minimises friction for vendoring into PodcastFetch and for third-party players.

### S32. Licence mechanics — MPL 2.0 FAQ https://www.mozilla.org/en-US/MPL/2.0/FAQ/ ; FOSSA Apache-2.0 https://fossa.com/blog/open-source-licenses-101-apache-license-2-0/ ; choosealicense MPL https://choosealicense.com/licenses/mpl-2.0/
- Type: policy
- Verified: snippet-only (fetch pending)
- Key facts:
  - MPL-2.0: file-level copyleft — modified MPL files must be shared; new files may be proprietary; express patent grant; GPL/Apache compatible via secondary licences.
  - Apache-2.0: express patent grant + termination on patent suit; MIT: no express patent grant.
- Relevance to AdVTT:
  - For a library vendored file-by-file into PodcastFetch, MPL's per-file obligation adds bookkeeping; Apache-2.0 gives the patent grant without copyleft; MIT is simplest. AGPL would deter player/app integration.

### S33. Podcast ad-skipping data — Sounds Profitable via Podnews https://podnews.net/press-release/ad-skipping-research ; Bumper https://wearebumper.com/blog/podcast-ad-skipping-isnt-nearly-as-bad-as-i-worried ; Pocket Casts forum https://forums.pocketcasts.com/forums/topic/automatic-ad-skipping/
- Type: dataset / blog / forum
- Verified: snippet-only (fetches pending)
- Key facts:
  - Sounds Profitable (2024): "46% of listeners say they 'always or often' skip ads"; 56–59% think ad load is "just right"; 73% expect 2–3 ads per episode.
- Relevance to AdVTT:
  - Manual skipping is already the norm for nearly half of listeners; annotation makes an existing behaviour precise rather than creating a new one.

### S34. Adblock Radio press (2019) — Vice https://vice.com/en_us/article/kz4gam/this-guy-made-an-ad-blocker-that-works-on-podcasts-and-radio ; InsideRadio https://www.insideradio.com/free/ad-blocking-for-podcasts-and-web-radio-may-soon-be-a-reality/article_ab5f24b6-e0ee-11e9-bc67-2f32e499da78.html ; repo https://github.com/adblockradio/adblockradio (fetch pending)
- Type: blog / repo
- Verified: snippet-only
- Key facts:
  - Storelli (physics PhD 2015): ads "exploit the weaknesses of many defenseless souls"; aim is media relying "less on ads and more on direct subscriptions".
  - Radio trade press covered it as a threat; no lawsuit reported.
- Relevance to AdVTT:
  - The prior open audio ad-blocker drew press but no legal action in 7 years; its moralising tone is a cautionary example — a neutral "metadata/accessibility" framing is likely to age better.

### S35. Podnews — "Spotify: unskippable ads for them, skipped ads for us?" — https://podnews.net/update/spotify-unskippable-or-not
- Type: trade press
- Verified: snippet-only
- Key facts:
  - Spotify sells unskippable podcast ads while its terms allow it to skip/remove others' ads in hosted shows.
- Relevance to AdVTT:
  - The ecosystem's grievance is *platform* power and consent asymmetry; a transparent, local, opt-in listener tool is on the other side of that line.

### S36. Sony Corp. of America v. Universal City Studios, 464 U.S. 417 (1984) — https://www.law.cornell.edu/supremecourt/text/464/417
- Type: legal
- Verified: fetched
- Key facts:
  - "Private, noncommercial time-shifting in the home" is fair use.
  - Staple-article rule: sale of copying equipment "does not constitute contributory infringement if the product is widely used for legitimate, unobjectionable purposes."
  - Court noted the Betamax has "a pause button and a fast-forward control" enabling ad-skipping; survey: "over 80% of the interviewees watched at least as much regular television as they had before."
  - "A challenge to a noncommercial use ... requires proof either that the particular use is harmful, or that if it should become widespread, it would adversely affect the potential market."
- Relevance to AdVTT:
  - Foundation for S1: the burden is on the rightsholder to show market harm from a noncommercial home use; the Court treated ad-skipping capability as an incidental feature, not a reason to condemn the device.

### S37. EFF case page — Newmark et al. v. Turner Broadcasting (outcome) — https://www.eff.org/cases/newmark-v-turner
- Type: legal (advocacy summary)
- Verified: fetched
- Key facts:
  - Studios dismissed against SONICblue after its 2003 bankruptcy and gave "covenants not to sue" to the five consumer plaintiffs.
  - 9 Jan 2004: court denied class conversion — "there was no longer a live issue between the studios and the five original ReplayTV owners."
  - Buyer Digital Networks North America removed Commercial Advance from future models; approx. 5,000 other owners "received no similar protection."
  - No ruling ever addressed commercial skipping on the merits.
- Relevance to AdVTT:
  - Confirms S10: the feature died commercially without an adverse ruling; the studios avoided a merits decision by conceding to the named users.

### S38. heise online — "Copyright: Springer vs Adblock Plus enters another round" (BGH I ZR 131/23, 31 Jul 2025) — https://www.heise.de/en/news/Copyright-Springer-vs-Adblock-Plus-enters-another-round-10505898.html
- Type: legal (tech press on primary ruling)
- Verified: fetched
- Key facts:
  - BGH faulted OLG Hamburg for not stating "which subject matter of protection" and which "relevant features conferring protection" it assumed, and for not weighing "the special features of a browser."
  - Protection of browser-generated code (DOM/CSSOM) "cannot be ruled out"; ad blockers "could potentially interfere with the exclusive right to it."
  - Remand: examine how browsers work, whether generated code is a protected program, whether blockers infringe reproduction/adaptation rights. No final holding that ad blockers infringe.
- Relevance to AdVTT:
  - The theory requires *in-memory alteration of program structures*. AdVTT never touches the player's or the file's program state; a metadata track consumed by the user's player is closer to a chapter file than to DOM manipulation (analysis, not advice).

### S39. Wettbewerbszentrale — BGH 19 Apr 2018, I ZR 154/16 (Adblock Plus lawful under UWG) — https://www.wettbewerbszentrale.de/bgh-sieht-adblock-plus-als-zulaessig-an/
- Type: legal (summary of primary ruling)
- Verified: fetched
- Key facts:
  - No targeted obstruction: Eyeo "verfolge in erster Linie eigene wirtschaftliche Interessen und habe keine Verdrängungsabsicht"; it does not manipulate the publisher's offering — "it rests with users" to run the software.
  - No aggressive practice: "nutze die Beklagte eine ihr etwaig zukommende Machtposition nicht aus."
  - Publishers may defend themselves technically (e.g., exclude ad-block users); the paid whitelist model was not prohibited.
- Relevance to AdVTT:
  - The German court's decisive facts — user runs the tool, publisher retains countermeasures, vendor not aiming to displace — all hold for a local annotator. A commercial whitelist (paid unblocking) was tolerated but is a reputational hazard AdVTT should avoid.

### S40. Podcast Index namespace issue #254 — proposed `<podcast:dynamic-ads-adjusted>` (opened 26 May 2021 by Adrian Machado) — https://github.com/Podcastindex-org/podcast-namespace/issues/254
- Type: repo (spec discussion)
- Verified: fetched
- Key facts:
  - Proposal: a boolean tag telling apps whether an episode's ads have been "adjusted" (dynamic insertion) — not ad ranges.
  - Proposer rejected the alternative of marking ad positions: "a tag to mark insertion points and duration of ads ... can be abused by ad blockers so adoption by hosts would be limited."
  - Closed as duplicate / "not planned"; no maintainer statement about ad blockers found on the page.
- Relevance to AdVTT:
  - Confirms there is no publisher-authored ad-range tag and that the ecosystem *anticipates* skip-abuse as the reason hosts would never publish one — AdVTT's client-side inference exists because the supply side will not label.
  - Also implies an opt-out tag (not a range tag) is the only cooperative signal hosts might adopt.

### S41. AntennaPod issue #4159 — "SponsorBlock integration" (16 May 2020) — https://github.com/AntennaPod/AntennaPod/issues/4159 ; predecessor #3382
- Type: repo (feature request)
- Verified: fetched
- Key facts:
  - Requests SponsorBlock-style skipping for podcast audio ads, opt-in with privacy warning; still open with label "Needs: Decision"; no maintainer verdict.
  - Earlier issue #3382 was closed because maintaining an ad-timestamp database was deemed out of scope for the app.
- Relevance to AdVTT:
  - A major FOSS podcast client has left this open for 6+ years rather than adopt or refuse — apps want the *data* but not the liability/maintenance of a shared database. An annotate-only library that a client can run locally answers exactly that hesitation.

### S42. TWiT.tv — Licensing — https://twit.tv/about/license
- Type: policy / legal
- Verified: fetched
- Key facts:
  - Shows are CC BY-NC-ND 4.0: redistribution allowed "as long as you attribute them to TWiT.tv and give a link to https://twit.tv"; "You may not distribute our shows for monetary gain of any kind."
  - Derivatives forbidden, explicitly including removing commercials, "without express written consent from TWiT.tv"; Club TWiT (paid) content: "Any copying ... modifying ... is strictly forbidden."
- Relevance to AdVTT:
  - A podcaster who *does* licence openly still prohibits ad-removal as a derivative — so a CC-BY-NC-ND show is usable as a public fixture for **annotation** (no derivative made) but not as a demo of **cutting** ads. Publishing timestamps about a TWiT episode is not a derivative of the audio (S19).
  - Confirms that ND-licensed feeds make the annotate-only posture materially safer than remove-and-redistribute.

### S43. US Copyright Office fair-use index summary — Authors Guild v. Google, 804 F.3d 202 (2d Cir. 2015) — https://www.copyright.gov/fair-use/summaries/authorsguild-google-2dcir2015.pdf
- Type: legal
- Verified: fetched
- Key facts:
  - Google Books is transformative because it provides "research tools" absent from the originals; snippets "provide information about a book's content rather than substituting for the book."
  - Snippet truncation and exclusions were "reasonable safeguards against market harm"; plaintiffs failed to show snippet display causes meaningful market harm.
- Relevance to AdVTT:
  - Direct support for emitting bounded evidence quotes and for the transcript-as-index step; also a design cue — cap quote length and never let quotes reconstruct the episode.

### S44. Directive (EU) 2019/790, Arts. 2(2), 3, 4 and Recital 18 — https://eur-lex.europa.eu/eli/dir/2019/790/oj
- Type: legal (primary text)
- Verified: fetched
- Key facts:
  - Art. 2(2): TDM "means any automated analytical technique aimed at analysing text and data in digital form."
  - Art. 3(1): research organisations/heritage institutions may copy works "for text and data mining for the purposes of scientific research."
  - Art. 4: exception for anyone unless rightholders reserved rights "by the use of machine-readable means, including metadata and terms and conditions" (Recital 18 for online content).
- Relevance to AdVTT:
  - Speech-to-text plus LLM classification of an audio file is squarely "automated analytical technique ... analysing ... data in digital form" — Art. 4 applies to AdVTT in the EU, conditioned on lawful access and honouring machine-readable reservations (TDMRep, S4).

### S45. Podnews — "Spotify's unskippable podcast ads, plus could they skip yours?" (17 Aug 2026) — https://podnews.net/article/spotify-unskippable-ads-and-auto-skips
- Type: trade press
- Verified: fetched
- Key facts:
  - Quotes Spotify for Creators Terms (spotify.com/us/legal/spotify-for-creators-terms) granting Spotify the right to "create derivative works from (including the right to transcribe ... modify and create derivative works."
  - Podnews: Spotify could "modify your show by stripping all the ads from your podcast" and host it as a Premium feature, uncompensated.
  - Media lawyer Gordon Firemark: could expose "podcasters and networks to claims that they've breached their contracts with sponsors."
- Relevance to AdVTT:
  - The sponsor-contract angle is the real commercial harm vector podcasters fear — *guaranteed impressions*; a listener-side annotation tool does not put the podcaster in breach, a platform stripping ads might.
  - Rhetorically: the dominant platform has reserved transcription and ad-modification rights over creators' audio; a local user tool doing less is hard to paint as the outlier.

### S46. YouTube Terms of Service (effective 15 Dec 2023) — https://www.youtube.com/t/terms
- Type: policy
- Verified: fetched
- Key facts:
  - Prohibits to "access, reproduce, download, distribute, transmit, broadcast, display, sell, license, alter, modify or otherwise use any part of the Service or any Content except" as permitted.
  - Prohibits to "circumvent, disable, fraudulently engage with, or otherwise interfere with any part of the Service ... including security-related features."
  - Prohibits automated access "except (a) in the case of public search engines, in accordance with YouTube's robots.txt file."
- Relevance to AdVTT:
  - Any future *video* mode that pulls from YouTube inherits ToS exposure regardless of copyright analysis; the podcast (RSS) mode has no equivalent contract. Keep YouTube ingestion out of the core, or leave it to the user's downloader (yt-dlp precedent, S25).

### S47. SponsorBlock README — https://github.com/ajayyy/SponsorBlock
- Type: repo
- Verified: fetched
- Key facts:
  - Code licence: GPL-3.0-or-later (README badge); the earlier "LGPL" note in S2 is corrected here.
  - Self-description: "an open-source crowdsourced browser extension to skip sponsor segments in YouTube videos"; also "intros, outros and reminders to subscribe."
  - No legal disclaimer or reference to YouTube's ToS on the README.
- Relevance to AdVTT:
  - Code GPL-3.0 + data CC BY-NC-SA (S2) is the SponsorBlock pattern; AdVTT wants permissive code for vendoring, so it should not copy SponsorBlock's licence split wholesale.
  - SponsorBlock's category vocabulary (sponsor / self-promotion / interaction reminder / intro / outro / preview / filler / highlight) is a de-facto community taxonomy AdVTT's vocabulary should map to.

### S48. Apple Media Services Terms and Conditions (US, last updated 15 Sep 2025) — https://www.apple.com/legal/internet-services/itunes/us/terms.html
- Type: policy
- Verified: fetched
- Key facts:
  - "You may use the Services and Content only for personal, noncommercial purposes"; "You may not tamper with or circumvent any security technology included with the Services or Content"; "You may not modify or use modified versions of such software."
  - No Apple-Podcasts-specific rule about RSS/third-party audio found in the document.
- Relevance to AdVTT:
  - Apple's terms restrict *its* software and DRM'd content; an RSS enclosure downloaded outside the Podcasts app is not "Content" delivered under these terms. A user running AdVTT on such a file is not modifying Apple software or circumventing security (analysis).

### S49. Megaphone (Spotify) — Terms and Policies page (privacy policy effective 1 Jul 2026; community guidelines) — https://megaphone.spotify.com/legal
- Type: policy
- Verified: fetched
- Key facts:
  - Contains a privacy policy and community guidelines addressed to publishers and advertisers; listeners appear only as a data-subject category. No listener-facing clause about downloading, transcribing, or skipping.
- Relevance to AdVTT:
  - The largest DAI host imposes no contractual restriction on listeners of the MP3s it serves; the only listener-side constraint is copyright law, not contract.

### S50. Art19 terms — https://art19.com/terms (404) — NOT FOUND
- Type: policy
- Verified: fetch failed (HTTP 404); no alternative located without search budget.
- Relevance to AdVTT: gap; Art19/Amazon listener terms unverified. Low importance — Art19 is a host serving open enclosures like Megaphone (S49).

### S51. Jellyfin Intro Skipper — README legal section — https://github.com/intro-skipper/intro-skipper
- Type: repo
- Verified: fetched
- Key facts:
  - Licence GPL-3.0. "No claim of ownership is made over any generated fingerprint or detection data by the plugin authors."
  - "Sharing or redistributing such data beyond purely local, personal use may violate the licenses, terms of service, or other agreements."
  - "This project is not affiliated with, endorsed by, or officially connected to the Jellyfin project or any media rights holder." Detects intros/credits, not commercials.
- Relevance to AdVTT:
  - Reusable disclaimer language and a precedent for *disclaiming ownership of derived detection data* while warning users about sharing it — the same posture AdVTT should take toward analysis.json.

### S52. Adblock Radio repository — https://github.com/adblockradio/adblockradio
- Type: repo
- Verified: fetched
- Key facts:
  - Licence MPL-2.0. Tagline: "A library to block ads on live radio streams and podcasts. Machine learning meets Shazam."
  - Output is a classification stream: it emits objects labelled "0-ads", "1-speech", "2-music", "9-unsure" — a library, not an auto-skipper.
  - Uses a central fingerprint DB (hotlist.sqlite) and models auto-updated from adblockradio.com/models/. Archived (read-only) 10 Apr 2021.
- Relevance to AdVTT:
  - Closest prior art in shape (library emitting a per-time class signal) chose MPL-2.0 and separated detection from skipping. It died of maintenance, not law.
  - Its central model/fingerprint server is a single point of failure and a liability surface AdVTT avoids by being local and model-agnostic.

### S53. Bumper — Dan Misener, "Podcast ad skipping isn't nearly as bad as I worried" (22 Feb 2026) — https://wearebumper.com/blog/podcast-ad-skipping-isnt-nearly-as-bad-as-i-worried
- Type: blog (industry analytics vendor)
- Verified: fetched
- Key facts:
  - "Most consumers tend to overstate how often they skip ads when asked hypothetical questions." 18% claim to skip "all the time" (Canadian Podcast Listener); 46% "always or often" (Sounds Profitable 2024).
  - Bumper clients see "90%+ ad retention rates" from Apple/Spotify/YouTube retention histograms; "Name another medium where ad retention is this high."
  - Longer ad breaks correlate with lower retention.
- Relevance to AdVTT:
  - Platforms already expose per-second retention to podcasters; a precise skipper would become visible in those histograms — so AdVTT's impact on the ecosystem is measurable by publishers, and the "downloads aren't affected" argument (S8) is only half true.
  - Suggests ad *length* is the listener's real grievance; an annotate-only track lets players show "ad: 90 s remaining" — a middle path between listening and skipping.

### S54. Pocket Casts community forum — "Automatic Ad Skipping" (Sep 2024 – Sep 2025) — https://forums.pocketcasts.com/forums/topic/automatic-ad-skipping/
- Type: forum
- Verified: fetched
- Key facts:
  - Staff (20 Sep 2024): "Ads can be inserted in different ways by podcast authors" — baked-in vs DAI makes detection hard.
  - Staff (3 Feb 2025): "Pocket Casts does not insert ads into podcasts at all"; (8 Sep 2025): "Pocket Casts respects choices made by podcast creators to support themselves."
  - Users cite SponsorBlock, zeroads.ai (external feed processing) and earsay.fm (ad-blocking plus creator compensation).
- Relevance to AdVTT:
  - A major (Automattic-owned) player has formally declined auto-skip on creator-respect grounds — the most explicit "community norm" statement found. Any client integrating AdVTT will face the same question; shipping opt-in metadata rather than skipping lets clients like this adopt display/"ad remaining" features without crossing their own line.
  - Commercial competitors (zeroads.ai, earsay.fm) already cut ads for pay; AdVTT's differentiation is openness and restraint, not capability.

### S55. Sounds Profitable / Signal Hill — "Ad Nauseam" (13 Jun 2024; n = 1,011 US weekly listeners 18+) — https://podnews.net/press-release/ad-skipping-research
- Type: dataset / press release
- Verified: fetched
- Key facts:
  - 46% "always or often" skip; the share "dropped substantially" when asked about the last episode actually heard. 28% listen to all ads — "highest among all media tested."
  - Skip reasons: lack of relevance 37%; unfamiliar product 28%. 56–59% say ad load is right; 73% expect 2–3 ads; most prefer 1–2 breaks.
  - Tom Webster: "Consumer tolerance for ads in podcasts isn't zero—they expect to hear ads."
- Relevance to AdVTT:
  - Industry's own framing: skipping is driven by relevance, not hostility; a classifier that labels *advertiser* lets a player skip only irrelevant categories — a less adversarial product story than blanket skipping.

### S56. UK CDPA 1988 s.29A (inserted 1 Jun 2014) — https://www.legislation.gov.uk/ukpga/1988/48/section/29A
- Type: legal (primary)
- Verified: fetched
- Key facts:
  - Copy permitted for "computational analysis of anything recorded in the work for the sole purpose of research for a non-commercial purpose", with acknowledgement unless impractical; lawful access required.
  - Transfer to another person or use for another purpose infringes; sale/hire makes it an infringing copy; contract terms preventing the copying are unenforceable.
- Relevance to AdVTT:
  - A UK hobbyist classifying ads for personal listening is not doing "research"; s.29A likely does not cover them and the UK has no private-copying exception since 2015 (S21 note). The transcript copy in the UK rests on the pragmatic point that no rightsholder has ever pursued personal transcription — a documented gap, not a clearance. Analysis, not advice.

### S57. Singapore Copyright Act 2021 ss.243–244 — https://sso.agc.gov.sg/Act/CA2021?ProvIds=P15-P28- (HTTP 403 to fetcher)
- Type: legal
- Verified: fetch failed (403); relying on S21 snippets.
- Relevance to AdVTT: gap on exact wording; secondary sources agree it permits computational data analysis for any purpose with lawful access and no onward supply of the copy.

### S58. Mozilla MPL 2.0 FAQ — https://www.mozilla.org/en-US/MPL/2.0/FAQ/
- Type: policy
- Verified: fetched
- Key facts:
  - "The copyleft applies to any files containing MPLed code"; "New files containing no MPL-licensed code are not Modifications."
  - Larger Work = "combination of Covered Software with a work governed by one or more Secondary Licenses" (GPL/LGPL/AGPL) if not marked "Incompatible With Secondary Licenses."
  - "May I combine MPL-licensed code and Apache? Yes."
- Relevance to AdVTT:
  - If PodcastFetch vendors AdVTT files verbatim under MPL, only *modified* AdVTT files must be published — workable, but Apache-2.0/MIT avoid the per-file audit entirely. Adblock Radio (S52) chose MPL; SponsorBlock chose GPL (S47).

### S59. OSI — "The most popular licenses for each language in 2023" (ClearlyDefined data, 21 Sep 2023; published 7 Dec 2023) — https://opensource.org/blog/the-most-popular-licenses-for-each-language-2023
- Type: dataset / blog
- Verified: fetched
- Key facts:
  - PyPI: MIT 29.14%, Apache-2.0 23.98%, BSD-2 6.25%, GPL-3.0 6.11%, no licence 23.69%. npm: MIT 53%, Apache 14.76%. Cargo: MIT and/or Apache 83.52%.
- Relevance to AdVTT:
  - Permissive licences are the Python norm; GPL-family is approx. 6%. Choosing MIT or Apache-2.0 matches ecosystem expectations for a library meant to be embedded in players.

### S60. CC BY-NC-SA 4.0 legal code — https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode
- Type: legal (licence text)
- Verified: fetched
- Key facts:
  - NonCommercial = "not primarily intended for or directed towards commercial advantage or monetary compensation."
  - Sui generis database rights: extraction/reuse of substantial portions allowed for NonCommercial purposes; incorporating into your own database makes it Adapted Material.
  - ShareAlike: adapter's licence "must be a Creative Commons license with the same License Elements, this version or later, or a BY-NC-SA Compatible License."
- Relevance to AdVTT:
  - If AdVTT ever publishes labels, CC BY-NC-SA would block commercial players (Pocket Casts, Overcast) from consuming them — SponsorBlock accepts that trade (S2). CC0 or ODbL would not. Decision deferred until a shared dataset is even contemplated.

### S61. AntennaPod issue #3382 — community ad-marker database proposal (4 Sep 2019; closed) — https://github.com/AntennaPod/AntennaPod/issues/3382
- Type: repo
- Verified: fetched (HTML view omitted comments; maintainer reasoning to be confirmed via API)
- Key facts:
  - Proposed: users mark ad start/end and share markers via a community database so others auto-skip. Closed; per #4159 (S41) because maintaining an ad-timestamp database was out of scope.
- Relevance to AdVTT:
  - FOSS clients reject *hosting the database*, not the concept; a local inference library sidesteps the objection.

### S62. VICE — "This Guy Made an Ad Blocker That Works on Podcasts and Radio" (25 Sep 2019) — https://www.vice.com/en/article/this-guy-made-an-ad-blocker-that-works-on-podcasts-and-radio/
- Type: press
- Verified: fetched
- Key facts:
  - Storelli: ads "exploit the weaknesses of many defenseless souls"; "dishonestly tempt people, steal their time and promise them a higher social status."
  - Wants to help the industry "develop alternative business models for radio and podcast lovers that do not want ads"; open-sourced it partly to pressure broadcasters toward self-regulation.
  - Detection: "speech recognition, acoustic fingerprinting, and machine learning" + crowdsourced ad DB; struggled with host-read ("native") ads; no broadcaster reaction reported.
- Relevance to AdVTT:
  - Host-read ads were the acknowledged failure mode of the acoustic approach in 2019 — exactly AdVTT's target, which is why an LLM-over-transcript design is a genuine advance rather than a re-tread.

### S63. AntennaPod issue #3382 — maintainer comments via GitHub API — https://api.github.com/repos/AntennaPod/AntennaPod/issues/3382/comments
- Type: repo
- Verified: fetched
- Key facts:
  - ByteHamster (5 Sep 2019): "Synchronizing this between multiple users is hard... We do not have (and do not plan to have) our own web servers. This would also have privacy implications"; "everything else is out of scope because it would need a web service."
- Relevance to AdVTT:
  - The objection was infrastructure and privacy, not ethics; a fully local library with no server fits what this client could accept.

### S64. AntennaPod issue #4159 — maintainer comments via GitHub API — https://api.github.com/repos/AntennaPod/AntennaPod/issues/4159/comments
- Type: repo
- Verified: fetched
- Key facts:
  - tonytamsf (16 May 2020): "We prefer to have the option to skip the beginning or ending"; (22 Oct 2020): integration "would have a bad look for the app and is bad for the ecosystem at this moment."
  - keunes (22 Oct 2020): the moral choice belongs to users; pointed to RSS funding tags (#4571) to compensate creators; (29 Oct 2020) moved discussion to the forum.
- Relevance to AdVTT:
  - The most-cited FOSS podcast client's stance: reputational ("bad look") and ecosystem concerns, softened by "user's moral choice" plus funding-tag support. AdVTT's design should make the "support the creator" path (podcast:funding / value) first-class so a client can adopt annotations without the "bad look."

### S65. Podcast Index namespace issue #254 — comment thread via GitHub API — https://api.github.com/repos/Podcastindex-org/podcast-namespace/issues/254/comments
- Type: repo (spec discussion)
- Verified: fetched
- Key facts:
  - ryan-lp (27 Jul 2023): "detecting dynamic ad insertion points is not difficult, app developers apparently just haven't realised it yet."
  - James Cridland (28 Jul 2023), on why hosts still won't publish ad positions: "while I'm sure my front door's lock is pickable ... I still lock it, rather than leave the front door wide open."
  - Closed 4 Mar 2026 by Marzal as part of archiving old issues, pointing to discussions #749 and #695 — not "duplicate" per se.
- Relevance to AdVTT:
  - The supply side has explicitly decided not to publish ad ranges *because* skipping would follow; AdVTT should not expect cooperative labelling and should not frame itself as a "standard" hosts will adopt. An *opt-out* signal is the only realistic cooperative hook.

### S66. Feist Publications, Inc. v. Rural Telephone Service Co., 499 U.S. 340 (1991) — https://www.law.cornell.edu/supremecourt/text/499/340
- Type: legal (primary)
- Verified: fetched
- Key facts:
  - "No one may claim originality as to facts." "The copyright in a factual compilation is thin." "Copyright does not extend to the facts themselves."
- Relevance to AdVTT:
  - Confirms S19 from the primary text: timestamps and labels about an episode are facts; a collection of them is at most a thin compilation owned by the collector.

### S67. Reed Smith — "Text and data mining in Singapore" (5 Feb 2024) — https://www.reedsmith.com/articles/text-and-data-mining-in-singapore/
- Type: legal (law-firm summary)
- Verified: fetched (statute itself returned 403, S57)
- Key facts:
  - s.243: "Using a computer program to identify, extract and analyze information or data from the work or recording."
  - s.244(2)(d): "lawful access to the material (the first copy) from which the copy is made"; s.244(2)(c): must not "supply the copy to any person other than for verifying results or collaborative research."
  - No commercial/non-commercial distinction.
- Relevance to AdVTT:
  - Singapore is the clearest statutory model of what AdVTT does — "identify, extract and analyze information ... from the ... recording" — with the same two conditions the design already implies: lawful source, no sharing of the copy.

### S68. Congressional Research Service RL34719 — Cartoon Network LP v. CSC Holdings (report dated 6 Jul 2009) — https://www.everycrsreport.com/reports/RL34719.html
- Type: legal (government summary of primary opinion)
- Verified: fetched (Justia opinion returned 403)
- Key facts:
  - Volition: the "person who actually presses the button to make the recording supplies the necessary element of volition."
  - A 1.2-second buffer is not embodiment for a "more-than-transitory duration."
  - Court treated the RS-DVR like a VCR the customer controls, not a video-on-demand service.
- Relevance to AdVTT:
  - Reinforces the user-as-actor framing (S1, S9): when the user runs `advtt classify episode.mp3`, the user, not the tool author, is the one "pressing the button."

### S69. Podnews — Apple Podcasts Connect Terms of Service (18 Feb 2026 diff) — https://podnews.net/article/apple-podcast-connect-tos-26
- Type: policy (via trade press diff)
- Verified: fetched
- Key facts:
  - Clause 8b: "You grant Apple the right to create transcripts of your Content ('Transcripts') and to (i) publicly display such Transcripts on Apple Podcasts and (ii) use your Content and/or Transcripts to generate chapters."
  - Opt-out: Apple "shall provide you with the ability ... to opt out of the public display of such Transcripts and chapters."
- Relevance to AdVTT:
  - Apple treats transcript generation as *its own* right needing a grant — because Apple publishes the text. AdVTT does not publish transcripts, which is the design line that keeps it on the analysis side rather than the publication side.
  - Apple's opt-out is only from *display*, not from creation — the same shape as AdVTT's proposed posture (analyse locally; never display/redistribute transcript text).

### S70. Podcasting 2.0 — `<podcast:txt>` tag documentation — https://podcasting2.org/docs/podcast-namespace/tags/txt
- Type: spec
- Verified: fetched
- Key facts:
  - Free-form text modelled on DNS TXT records; optional `purpose` attribute; registered values include `verify`, `applepodcastsverify`, `ai-content` (boolean indicating AI-generated content).
  - Allowed at channel and item level; "free form nature" permits undocumented purposes without formal approval.
- Relevance to AdVTT:
  - A podcaster-side opt-out can ship today with zero spec process: e.g. `<podcast:txt purpose="tdm-reservation">1</podcast:txt>` (mirroring TDMRep values, S4) — AdVTT can honour it immediately and propose registration later.

### S71. Podcasting 2.0 — `<podcast:value>` tag documentation — https://podcasting2.org/docs/podcast-namespace/tags/value
- Type: spec
- Verified: fetched
- Key facts:
  - Attributes `type`, `method` (required), `suggested`; `<podcast:valueRecipient>` children; channel or item level; value time splits are a separate tag.
  - Supported by 15 apps, 16 publishing tools, 10 services (per docs page).
  - The docs do *not* frame it as an alternative to advertising — that framing is the community's (S26), not the spec's.
- Relevance to AdVTT:
  - When an episode carries `podcast:value`/`podcast:funding`, AdVTT's output can include a `support` pointer so players can pair "skip" with "boost"; do not overstate V4V adoption (15 apps).

### S72. choosealicense.com — Apache License 2.0 — https://choosealicense.com/licenses/apache-2.0/
- Type: policy
- Verified: fetched
- Key facts:
  - "A permissive license whose main conditions require preservation of copyright and license notices. Contributors provide an express grant of patent rights."
  - Conditions: licence/copyright notice; "State changes" (modified files "must carry prominent notices stating that You changed the files"). Limitations: trademark use not granted; no warranty/liability.
- Relevance to AdVTT:
  - The "state changes" condition is the only vendoring cost versus MIT; the trademark limitation is useful — it lets the author keep the AdVTT name distinct from forks that *do* cut audio.

### S73. Directive 96/9/EC (legal protection of databases), Arts. 7 and 10 — https://eur-lex.europa.eu/eli/dir/1996/9/oj
- Type: legal (primary)
- Verified: fetched
- Key facts:
  - Art. 7(1): sui generis right for a maker showing "a substantial investment in either the obtaining, verification or presentation of the contents" against extraction/re-utilisation of a substantial part.
  - Art. 7(5): repeated systematic extraction of insubstantial parts that conflicts with normal exploitation is prohibited. Art. 10: 15 years, renewed by substantial change.
- Relevance to AdVTT:
  - In the EU, any *shared* AdVTT label set would itself attract a database right for AdVTT (a benefit) — but the podcaster has no database right in their own episode's ad positions, since they never compiled them. Timestamps remain the annotator's facts to give away.

### Failed fetches (logged)
- Fox v. Dish 2014 opinion PDF — https://cdn.ca9.uscourts.gov/datastore/opinions/2014/01/24/13-56818.pdf → 404 (S11 stays snippet-only).
- Akin Gump Bartz summary → 403 (S16 stays snippet-only).
- Art19 terms → 404 (S50); Singapore SSO → 403 (S57, covered by S67); Justia Cartoon Network → 403 (covered by S68).
- copyright.gov HathiTrust summary PDF and bunka.go.jp Japan AI/copyright PDF were saved as binaries; text extracted locally with pdftotext — see S74–S75.

### S74. US Copyright Office Fair Use Index — Authors Guild v. HathiTrust, 755 F.3d 87 (2d Cir. 2014) — https://www.copyright.gov/fair-use/summaries/authorsguild-hathitrust-2dcir2014.pdf
- Type: legal (official summary)
- Verified: fetched (PDF text extracted locally with pdftotext)
- Key facts:
  - Full-text search database "quintessentially transformative": "the result of a word search is different in purpose, character, expression, meaning, and message from the page (and the book)."
  - Copies "reasonably necessary" for the service and for disaster mitigation; full-text search "posed no harm to any existing or potential traditional market."
  - Retaining both text and image copies was reasonable because text copies "were required for text searching and text-to-speech capabilities."
- Relevance to AdVTT:
  - Closest US analogue to keeping a machine transcript solely as an index for classification: transformative purpose, no market substitution, retention justified by function. Also an accessibility framing (text-to-speech / print-disabled) that AdVTT's `kind="metadata"` track can borrow honestly — the same labels that enable skipping enable "warn me / describe what this segment is."

### S75. Agency for Cultural Affairs (Japan) — "General Understanding on AI and Copyright in Japan" overview (Art. 30-4) — https://www.bunka.go.jp/english/policy/copyright/pdf/94055801_01.pdf
- Type: legal (official guidance)
- Verified: fetched (PDF text extracted locally)
- Key facts:
  - Art. 30-4 permits "Exploitation of a copyrighted work not for enjoyment of the thoughts or sentiments expressed in the copyrighted work," e.g. data analysis / AI training, without consent.
  - Does not apply where "there is also the purpose of enjoyment", nor in "cases that would unreasonably prejudice the interests of the copyright owner" (e.g. copying a database sold for analysis, or bypassing technical measures).
  - Commerciality is not the test: even "non-commercial" or "research" use needs permission if an enjoyment purpose coexists.
- Relevance to AdVTT:
  - Japan's test maps well: the *transcription-for-classification* step is non-enjoyment; but the user then *enjoys* the episode. The guidance keys on the purpose of the *copy* (the transcript), which is analytic — supportive, with the caveat that the same user also listens (analysis, not advice).
  - The "technical measures" proviso is another reason to honour TDMRep-style reservations (S4, S44).

### Planned fetches — DONE (all candidates above were fetched or logged as failed; see S36–S75 and 'Failed fetches')

## Synthesis

**Q1 — US ad-skipping precedents.** The only appellate decision on *automatic* ad-skipping is Fox v. Dish (S1, S11). It holds that commercial-skipping "does not implicate Fox's copyright interest", that market-harm analysis must "exclude consideration of AutoHop", and that "AutoHop, standing alone, does not infringe"; the user's recording is Sony fair use (S36) and Dish is not the direct copier because the copy is made "only in response to the user's command" (S1, S9, S68). Three facts the court recited are design-relevant: AutoHop shipped **off by default**, it **did not delete** ads, and markers travelled in a **separate "announcement" file** with "the program content ... not altered in any way" (S1). The only exposure was Dish's own QA copies. ReplayTV (S5, S10, S37) never reached a merits ruling — SONICblue went bankrupt in 2003 and the studios bought off the consumer plaintiffs with covenants not to sue; the buyer removed Commercial Advance. The 2016 Fox–Dish settlement was a **7-day window**, not a ban (S12). Sony itself treated fast-forward as incidental and put the burden of proving harm on the rightsholder (S36). Podcast caveat: for host-read ads the podcaster usually owns the ad copy, so Fox's "we don't own the ads" limb weakens; the Sony limb (a lawful copy, partially unheard, is not infringement) does not depend on it. *All of this is analysis, not legal advice.*

**Q2 — Ad-blocking precedents.** Germany: BGH 2018 (S13, S39) held shipping Adblock Plus lawful under unfair-competition law because "it rests with users" and publishers keep countermeasures; BGH 31 Jul 2025 (S6, S14, S38) remanded a *copyright* theory that hinges on ad blockers altering browser-generated program structures (DOM/CSSOM) — no finding of infringement yet; post-remand status unchecked (gap). No US court decision on browser ad blockers surfaced (gap; likely none on the merits). YouTube enforces via ToS, not litigation (S15, S46). **Annotation vs blocking:** no precedent addresses time-metadata specifically (gap), but every live theory — program adaptation (S38), derivative works (S42 TWiT ND clause), ToS "alter, modify" (S46) — requires *changing* the work or a program. A side-car VTT changes neither, and Fox v. Dish described exactly that architecture without concern (S1). SponsorBlock has distributed segment metadata about YouTube videos since 2019 under CC BY-NC-SA with no reported legal action (S2, S47).

**Q3 — Transcripts and derived data.** Machine transcription for analysis sits on strong ground where the source copy is lawful: HathiTrust/Google Books (S43, S74) treat full-text indexing as "quintessentially transformative" with snippets giving "information about" the work; Bartz (S16) blesses format-shifting lawfully bought works but condemns pirated libraries; Kadrey (S17) makes market harm dispositive. Statutory TDM: EU Art. 4 (S44) covers "any automated analytical technique" for anyone, subject to lawful access and a machine-readable opt-out (TDMRep, S4); Singapore s.244 (S67) is the cleanest fit ("identify, extract and analyze information ... from the ... recording", any purpose, no onward supply); Japan Art. 30-4 (S75) permits non-enjoyment analytic copies; the **UK s.29A is non-commercial *research* only** (S56) — a UK hobbyist is probably outside it (gap). Every regime forbids *redistributing the copy* — so transcripts must stay local. **Timestamps/labels are facts** (S19, S66) — no copyright in them belongs to the podcaster; an EU database right, if any, would belong to the annotator (S73). **Short evidence quotes** (5–15 words) match the Google Books snippet logic (S43) provided they cannot reconstruct the work; they are also the weakest link if a shared dataset ever emerges, because thousands of quotes per show start to look like a transcript.

**Q4 — Terms of service.** Apple (S48, S69), Spotify (S45), Megaphone (S49) and Acast+ (S24) terms bind *creators* and users of *their apps/services*; no listener-facing clause restricting transcription or skipping of an RSS enclosure was found (S49 explicitly none; Art19 unverified, S50). Apple reserves a right to "create transcripts ... and generate chapters" from every show (S69); Spotify's creator terms reserve rights "to transcribe ... modify and create derivative works" and it is testing a "Skip ahead" button on others' ads and even Patreon asks (S7, S45). YouTube's ToS forbids "alter, modify" and "circumvent, disable ... interfere" (S46) — relevant only to a future video mode. Paid feeds (Acast+, Club TWiT) carry no-modification/no-copy terms (S24, S42).

**Q5 — Community norms.** Precedents: SponsorBlock (GPL-3 code, CC BY-NC-SA data, S2/S47); intro-skipper (GPL-3, local-only, disclaims ownership of detection data, warns against sharing it, S51); Adblock Radio (MPL-2.0, library emitting ad/speech/music classes, "counter power" framing, archived 2021, S3/S52/S62); youtube-dl survived RIAA (S25). Client stances: **Pocket Casts formally declines auto-skip** — "respects choices made by podcast creators to support themselves" (S54); AntennaPod left SponsorBlock integration open for 6 years, maintainers calling it "a bad look ... bad for the ecosystem" while noting "the moral choice belongs to users" and pointing to funding tags (S41, S63, S64). Supply side: Podcast Index contributors refused an ad-range tag because it "can be abused by ad blockers" — "I still lock [my door]" (S40, S65). Industry data: 46% say they "always or often" skip but actual retention is often "90%+" (S53, S55); measurement is download-based so skipping does not lower counted impressions (S30) but *is* visible in retention histograms (S53). Value4Value exists (S26, S71) but only approx. 15 apps support it. The loudest 2026 controversy is Spotify skipping others' ads (S7, S35, S45) — a platform/consent problem, not a listener-tool problem.

**Q6 — Release design.** Evidence favours: annotate-only (S1, S38, S42, S51); default-off skipping (S1); local-only transcripts and no shared label DB at launch (S21, S51, S56, S63); default-exclude house/membership/V4V asks (S7, S64); honour existing opt-outs — TDMRep (S4, S44) and a `podcast:txt` purpose (S70) — rather than inventing new ones (S29). Opt-out precedents: robots.txt is the only widely honoured signal; TDMRep is law-anchored in the EU; C2PA is provenance only (S29).

**Q7 — Licences.** PyPI is 29% MIT / 24% Apache-2.0 / 6% GPL (S59); Apache-2.0 adds an express patent grant and a trademark carve-out at the cost of "state changes" notices (S72); MPL-2.0's file-level copyleft is vendoring-tolerant but adds per-file audit (S58); AGPL/GPL would block adoption by the very clients whose hesitation is reputational (S64). Fixtures: full transcripts of real episodes are copies no TDM regime lets you redistribute (S21, S56, S67) and would breach ND licences even for CC shows (S42).

**Contradictions/gaps.** (a) Fox says skipping isn't a copyright harm; podcasters' real harm is sponsor-contract impressions (S45) — a business harm, not a legal one. (b) HN says skipping "doesn't cost creators anything" (S8) vs Bumper showing retention is measured per-second (S53). (c) OLG Hamburg post-remand status, any US ad-blocker ruling, UK personal-use coverage, Art19 terms — unverified.

## Implications for AdVTT

1. **Release posture: "annotation tool", never "ad blocker".** Emit metadata only; never write modified audio; no `--cut` in the core (S1, S38, S42, S51). Name, README and CLI verbs should say classify/annotate. Any skip UI lives in players and ships **off by default** (S1, S54).
2. **Two-tier output with a hard privacy line.** The distributable track (`.vtt`) carries times, kind, confidence, advertiser label and provenance — facts only (S19, S66). Evidence quotes (≤ approx. 15 words) live in the *local* `analysis.json` and are excluded from anything shared by default (S43, S21). Never emit transcript text (S56, S67, S69).
3. **Source policy in code and docs:** operate on RSS enclosures the user lawfully holds; no built-in fetching from Apple/Spotify/YouTube (S16, S46, S48). State that paid/private feeds may carry contractual terms the user is responsible for (S24, S42).
4. **Honour opt-outs before transcribing:** check TDMRep (`tdm-reservation` header / `/.well-known/tdmrep.json`) on the enclosure host (S4, S44) and a feed-level `<podcast:txt purpose="tdm-reservation">1</podcast:txt>` (S70); log and skip. Propose registration of that purpose with Podcasting 2.0 as an *opt-out*, not an ad-range tag, which the community has rejected (S40, S65).
5. **Vocabulary change:** add explicit HOUSE / SELF_PROMOTION and FUNDING_ASK (Patreon, membership, V4V) classes that are **never in the default skip set**; map others to SponsorBlock's categories (sponsor, interaction reminder, intro/outro, preview) so players reuse existing UI (S7, S47, S64). Surface `podcast:funding`/`podcast:value` in output so a player can pair "skip" with "support" (S26, S71).
6. **Consider "ad remaining" over "skip" as the flagship player affordance:** listeners' grievance is length and relevance, not ads per se (S53, S55); a countdown/"what is this segment" display is accessibility-shaped (S74) and is something Pocket-Casts-like clients could adopt without crossing their stated line (S54).
7. **Licence: Apache-2.0** for the CLI/library (patent grant, trademark carve-out lets the author police forks that cut audio, permissive enough for vendoring into PodcastFetch and any player; S59, S72). MIT is acceptable if patent/trademark language is unwanted; avoid AGPL/GPL (S64) and MPL's per-file audit (S58).
8. **Keep real-episode fixtures out of the public repo.** Publish only: enclosure URL + content hash + hand-labelled `.vtt` (facts) + a script that regenerates the transcript locally from the user's own download; transcripts stay in a private fixtures repo (S21, S25, S42, S56). If a public eval set is wanted, record it or use CC-BY/CC0 audio — note that even CC BY-NC-ND shows (TWiT) forbid derivatives, so transcripts of them cannot be redistributed either (S42).
9. **No shared label database at launch.** If one is ever added: opt-in upload, label-only (no quotes), licence CC BY-NC-SA (SponsorBlock precedent) or CC0 (to let commercial players consume), and expect the sui generis right to sit with AdVTT (S2, S60, S73).
10. **Disclaimer and framing borrowed from intro-skipper** — "No claim of ownership ... over any generated ... detection data"; "not affiliated with ... any media rights holder"; sharing derived data "may violate ... terms" — and avoid Adblock Radio's moralising register (S51, S62). Add an explicit "this is not legal advice; laws differ (UK s.29A is research-only)" note (S56).
11. **Differentiate from Spotify's 'Skip ahead'** in launch messaging: local, opt-in, transparent, creator-ask-safe, no platform stripping ads from other people's shows (S7, S45).

## Open questions / things that need an experiment
- **OLG Hamburg post-remand (Axel Springer v. Eyeo)** — check for a 2026 judgment; if browser DOM alteration is held infringing, confirm AdVTT's side-car design remains outside it (S38).
- **US browser-ad-blocker case law** — none found; confirm with a targeted search when budget allows.
- **UK personal-use gap** — is there any exception covering a UK hobbyist's transcript? Likely no; decide whether docs should say so (S56).
- **TDMRep adoption on podcast hosts** — experiment: HEAD the enclosure hosts of the four fixtures (and top-10 hosts: Megaphone, Acast, Art19, Libsyn, Buzzsprout, Spreaker, Omny, Transistor, RSS.com, Anchor) for `tdm-reservation` and `/.well-known/tdmrep.json`; expect zero today, but this establishes the baseline for the honour-the-signal claim (S4).
- **`podcast:txt` opt-out proposal** — open a Podcasting 2.0 Discussion proposing `purpose="tdm-reservation"` (or `"no-analysis"`) and see whether hosts/apps engage; issue #254's rejection was of *ad ranges*, not opt-outs (S40, S65, S70).
- **Evidence-quote length vs recall** — experiment: cap quotes at 8, 12, 15 words and measure `boundary_err_sec` and verbatim-match failure rate; pick the shortest cap that preserves the ≤ 3 s boundary gate.
- **Retention-histogram visibility** — could an AdVTT-driven skip be detected by Bumper-style analytics? Not a legal issue but shapes the "downloads unaffected" claim (S53).
- **Art19/Amazon listener terms** — locate and read (S50).
- **Fixtures replacement** — find 4 CC-BY or CC0 podcasts with host-read sponsor segments to rebuild a public eval set; TWiT is ND so unsuitable for transcript redistribution (S42).
