/**
 * Table partagée des liens partenaires / affiliations — FacturKit 2027
 * Fichier public sans secret ni PII.
 *
 * MODE D'EMPLOI (activation 1 fichier -> met à jour les 52 pages : comparateur,
 * simulateur URSSAF et les 50 pages /metiers/*.html simultanément) :
 * Remplacez simplement les chaînes vides "" ci-dessous par vos URLs affiliées
 * validées (Affilae, Axonaut, Sellsy). Tant qu'un slot reste vide, le lien
 * officiel natif du logiciel reste actif sans tracking.
 */
(function (global) {
  "use strict";

  var PA_AFFILIATE_MAP = {
    "affilae-indy": "",
    "affilae-tiime": "",
    "affilae-pennylane": "",
    "affilae-qonto": "",
    "affilae-shine": "",
    "affilae-abby": "",
    "direct-axonaut": "",
    "direct-sellsy": ""
  };

  var PA_SOLUTIONS = {
    indy: {
      name: "Indy",
      slot: "affilae-indy",
      url: "https://www.indy.fr/",
      badge: "PA immatriculée DGFiP (09/01/2026)",
      price: "Facturation & compte pro 0 € · Compta dès 16 €/mois",
      summary: "Idéal professions libérales, indépendants BNC, micro-entreprises, EI et SASU/EURL cherchant comptabilité automatisée + facturation électronique."
    },
    tiime: {
      name: "Tiime",
      slot: "affilae-tiime",
      url: "https://www.tiime.fr/",
      badge: "PA immatriculée DGFiP (18/12/2025)",
      price: "Facturation Factur-X 0 € · Compte pro dès 9,99 €/mois",
      summary: "Réception & émission Factur-X gratuites pour indépendants/TPE, synchronisation fluide avec plus de 2 500 cabinets experts-comptables."
    },
    pennylane: {
      name: "Pennylane",
      slot: "affilae-pennylane",
      url: "https://www.pennylane.com/fr/",
      badge: "PA immatriculée DGFiP (11/12/2025)",
      price: "Socle micro gratuit · Plans PME & cabinets sur devis",
      summary: "Référence des PME en croissance et des cabinets comptables : pré-comptabilité, rapprochement bancaire temps réel et flux PA natifs."
    },
    qonto: {
      name: "Qonto",
      slot: "affilae-qonto",
      url: "https://qonto.com/fr",
      badge: "PA immatriculée DGFiP (18/12/2025)",
      price: "Compte pro + facturation dès 9 € HT/mois",
      summary: "Compte pro tout-en-un avec dépôt de capital, cartes multi-équipes, gestion des notes de frais et réception/émission Factur-X intégrée."
    },
    shine: {
      name: "Shine",
      slot: "affilae-shine",
      url: "https://www.shine.fr/",
      badge: "Compte pro + Shine Facture conforme",
      price: "Offre Free 0 € · Plans pro dès 11 € HT/mois",
      summary: "Compte pro orienté indépendants, artisans et micro-entreprises avec calcul URSSAF intégré et outil de facturation simple."
    },
    abby: {
      name: "Abby",
      slot: "affilae-abby",
      url: "https://www.abby.gg/",
      badge: "Logiciel micro-entreprise & Factur-X",
      price: "Plan gratuit · Plans Pro dès 10 €/mois",
      summary: "Conçu spécifiquement pour les micro-entrepreneurs : devis, factures, livre des recettes, suivi des seuils TVA 293 B et déclarations URSSAF."
    },
    axonaut: {
      name: "Axonaut",
      slot: "direct-axonaut",
      url: "https://axonaut.com/",
      badge: "PA immatriculée DGFiP (08/01/2026)",
      price: "CRM + Facturation + Trésorerie dès 49 €/mois",
      summary: "ERP/CRM français tout-en-un adapté aux TPE/PME de services, artisans et agences ayant besoin de devis, gestion de projet et PA native."
    },
    sellsy: {
      name: "Sellsy",
      slot: "direct-sellsy",
      url: "https://go.sellsy.com/",
      badge: "PA immatriculée DGFiP (24/12/2025)",
      price: "Suite CRM + Facturation PME dès 39 €/utilisateur/mois",
      summary: "Suite commerciale et facturation électronique robuste pour PME B2B, équipes commerciales multi-utilisateurs et suivi de trésorerie."
    }
  };

  function applyFacturKitAffiliates(root) {
    var scope = root || global.document;
    if (!scope || !scope.querySelectorAll) return;
    var links = scope.querySelectorAll("a[data-affiliate-slot]");
    for (var i = 0; i < links.length; i++) {
      var slot = links[i].getAttribute("data-affiliate-slot");
      if (slot && PA_AFFILIATE_MAP[slot]) {
        links[i].setAttribute("href", PA_AFFILIATE_MAP[slot]);
        links[i].setAttribute("rel", "noopener noreferrer sponsored");
      }
    }
  }

  global.PA_AFFILIATE_MAP = PA_AFFILIATE_MAP;
  global.PA_SOLUTIONS = PA_SOLUTIONS;
  global.applyFacturKitAffiliates = applyFacturKitAffiliates;

  if (global.document) {
    if (global.document.readyState === "loading") {
      global.document.addEventListener("DOMContentLoaded", function () {
        applyFacturKitAffiliates(global.document);
      });
    } else {
      applyFacturKitAffiliates(global.document);
    }
  }
})(typeof window !== "undefined" ? window : globalThis);
