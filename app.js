/**
 * Logique interactive de la vitrine YGN — FacturKit 2027
 * Sans dépendance externe, 100% compatible desktop & mobile (390px+).
 */
(function () {
  "use strict";

  const cfg = window.FACTURKIT_CONFIG || {};

  function isValidLuhn(digits) {
    const clean = (digits || "").replace(/\s+/g, "");
    if (!/^\d{9}$|^\d{14}$/.test(clean)) return false;
    let sum = 0;
    let shouldDouble = false;
    for (let i = clean.length - 1; i >= 0; i--) {
      let d = parseInt(clean.charAt(i), 10);
      if (shouldDouble) {
        d *= 2;
        if (d > 9) d -= 9;
      }
      sum += d;
      shouldDouble = !shouldDouble;
    }
    return sum % 10 === 0;
  }

  function syncPaymentButtons() {
    if (!cfg.stripeLinks) return;
    document.querySelectorAll("[data-stripe-slot]").forEach(function (el) {
      const slotKey = el.getAttribute("data-stripe-slot");
      const url = cfg.stripeLinks[slotKey];
      if (url && url.startsWith("https://")) {
        el.setAttribute("href", url);
      }
    });

    document.querySelectorAll("[data-paypal-slot]").forEach(function (btn) {
      const slotKey = btn.getAttribute("data-paypal-slot");
      const ppLink = cfg.paypalSlotLinks && cfg.paypalSlotLinks[slotKey];
      if (ppLink) {
        btn.textContent = "Payer via PayPal (" + cfg.slots[slotKey].priceEur + " € net) ou Devis B2B";
      }
    });
  }

  function setupModal() {
    const modal = document.getElementById("b2b-modal");
    if (!modal) return;

    const closeBtn = document.getElementById("b2b-modal-close");
    const companyInput = document.getElementById("b2b-company");
    const sirenInput = document.getElementById("b2b-siren");
    const sirenStatus = document.getElementById("b2b-siren-status");
    const slotSelect = document.getElementById("b2b-slot-select");
    const quotePreview = document.getElementById("b2b-quote-preview");
    const copyBtn = document.getElementById("b2b-copy-btn");
    const printBtn = document.getElementById("b2b-print-btn");
    const paypalDirectWrap = document.getElementById("b2b-paypal-direct-wrap");
    const paypalDirectLink = document.getElementById("b2b-paypal-direct-link");
    const stripeFallbackLink = document.getElementById("b2b-stripe-instant-link");

    function renderQuote() {
      const slotKey = slotSelect.value || "slot2";
      const slot = (cfg.slots && cfg.slots[slotKey]) || {
        code: "SLOT 02",
        title: "Studio Factur-X Local 2027",
        priceEur: 49,
        reference: "FK27-S02-STUDIO",
        summary: ""
      };
      const company = (companyInput.value || "").trim() || "[Raison sociale / Nom professionnel]";
      const sirenRaw = (sirenInput.value || "").replace(/\s+/g, "");
      let sirenLine = "Non renseigné (à compléter pour comptabilité B2B)";

      if (sirenRaw.length > 0) {
        if (isValidLuhn(sirenRaw)) {
          sirenStatus.textContent = "✓ Numéro SIREN/SIRET valide (contrôle Luhn conforme)";
          sirenStatus.style.color = "#047857";
          sirenLine = sirenRaw + " (Luhn vérifié)";
        } else {
          sirenStatus.textContent = "Vérifiez la saisie : 9 chiffres (SIREN) ou 14 chiffres (SIRET) valides requis";
          sirenStatus.style.color = "#B45309";
          sirenLine = sirenRaw + " (à vérifier)";
        }
      } else {
        sirenStatus.textContent = "Optionnel — contrôle algorithmique Luhn instantané.";
        sirenStatus.style.color = "#64748B";
      }

      const today = new Date().toISOString().slice(0, 10);
      const quoteNum = "DEVIS-FK27-" + today.replace(/-/g, "") + "-" + slot.code.replace(/\s+/g, "");

      const ppLink = cfg.paypalSlotLinks && cfg.paypalSlotLinks[slotKey];
      if (ppLink) {
        paypalDirectWrap.hidden = false;
        paypalDirectLink.href = ppLink;
        paypalDirectLink.textContent = "Régler " + slot.priceEur + ",00 € net avec PayPal →";
      } else {
        paypalDirectWrap.hidden = true;
      }

      if (cfg.stripeLinks && cfg.stripeLinks[slotKey]) {
        stripeFallbackLink.href = cfg.stripeLinks[slotKey];
        stripeFallbackLink.textContent =
          "Accès immédiat CB / Apple Pay / Link (" + slot.priceEur + " € net — Facture Stripe auto)";
      }

      quotePreview.textContent = [
        "PROPOSITION COMMERCIALE / DEVIS B2B — " + (cfg.brand || "YGN — FacturKit"),
        "Référence : " + quoteNum + " | Date d'émission : " + today + " | Validité : 30 jours",
        "------------------------------------------------------------------------",
        "ÉMETTEUR : YGN — FacturKit (Édition logicielle & outillage numérique B2B)",
        "CLIENT   : " + company,
        "SIREN    : " + sirenLine,
        "------------------------------------------------------------------------",
        "DÉSIGNATION (" + slot.reference + ") :",
        slot.code + " — " + slot.title,
        "Nature de l'opération : Fourniture de contenus & outils numériques B2B",
        "Livraison : Téléchargement HTTPS immédiat (archive .zip signée SHA-256)",
        "------------------------------------------------------------------------",
        "MONTANT TOTAL NET : " + slot.priceEur + ",00 EUR",
        "Régime TVA        : Prix net — TVA non applicable, art. 293 B du CGI",
        "------------------------------------------------------------------------",
        "RÈGLEMENT IMMÉDIAT AVEC FACTURE B2B AUTOMATIQUE (SIREN INCLUS) :",
        cfg.stripeLinks && cfg.stripeLinks[slotKey] ? cfg.stripeLinks[slotKey] : ""
      ].join("\n");
    }

    function openModal(slotKey) {
      if (slotKey && slotSelect) {
        slotSelect.value = slotKey;
      }
      renderQuote();
      modal.hidden = false;
      document.body.style.overflow = "hidden";
      if (companyInput) companyInput.focus();
    }

    function closeModal() {
      modal.hidden = true;
      document.body.style.overflow = "";
    }

    document.querySelectorAll("[data-paypal-slot]").forEach(function (btn) {
      btn.addEventListener("click", function (ev) {
        ev.preventDefault();
        const slotKey = btn.getAttribute("data-paypal-slot") || "slot2";
        openModal(slotKey);
      });
    });

    if (closeBtn) closeBtn.addEventListener("click", closeModal);
    modal.addEventListener("click", function (ev) {
      if (ev.target === modal) closeModal();
    });
    document.addEventListener("keydown", function (ev) {
      if (ev.key === "Escape" && !modal.hidden) closeModal();
    });

    [companyInput, sirenInput, slotSelect].forEach(function (el) {
      if (el) el.addEventListener("input", renderQuote);
      if (el) el.addEventListener("change", renderQuote);
    });

    if (copyBtn) {
      copyBtn.addEventListener("click", function () {
        const text = quotePreview.textContent || "";
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(text).then(function () {
            const orig = copyBtn.textContent;
            copyBtn.textContent = "✓ Devis copié dans le presse-papiers";
            setTimeout(function () {
              copyBtn.textContent = orig;
            }, 2200);
          });
        }
      });
    }

    if (printBtn) {
      printBtn.addEventListener("click", function () {
        window.print();
      });
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      syncPaymentButtons();
      setupModal();
    });
  } else {
    syncPaymentButtons();
    setupModal();
  }
})();
