/**
 * Configuration publique — YGN — FacturKit 2027
 * IMPORTANT SÉCURITÉ : Fichier client public. Ne jamais insérer de clé secrète,
 * d'IBAN personnel ou d'adresse privée dans ce fichier.
 */

// 1-VARIABLE PAYPAL : Renseignez ici votre URL PayPal.me ou lien PayPal NCP
// (ex: "https://paypal.me/VotreIdentifiant") pour activer le bouton PayPal direct.
// Si laissé vide (""), le bouton secondaire "Devis B2B / Autre règlement" ouvre le module
// instantané d'édition de Devis B2B / Bon de commande avec contrôle SIREN.
const PAYPAL_CHECKOUT_URL = "";

window.FACTURKIT_CONFIG = {
  brand: "YGN — FacturKit",
  productSuite: "FacturKit 2027",
  publicSiteUrl: "https://yannabadie.github.io/facturkit-2027/",
  taxNotice: "Prix nets — TVA non applicable, art. 293 B du CGI",
  activePaymentMethods: [
    "Carte Bancaire (CB / Visa / Mastercard)",
    "Apple Pay",
    "Amazon Pay",
    "Klarna",
    "Link",
    "Bancontact"
  ],
  paypalCheckoutUrl: PAYPAL_CHECKOUT_URL,
  paypalSlotLinks: {
    slot1: PAYPAL_CHECKOUT_URL ? `${PAYPAL_CHECKOUT_URL.replace(/\/$/, "")}/19EUR` : "",
    slot2: PAYPAL_CHECKOUT_URL ? `${PAYPAL_CHECKOUT_URL.replace(/\/$/, "")}/49EUR` : "",
    slot3: PAYPAL_CHECKOUT_URL ? `${PAYPAL_CHECKOUT_URL.replace(/\/$/, "")}/119EUR` : ""
  },
  stripeLinks: {
    slot1: "https://buy.stripe.com/3cIaEWfnS8ifbTBdXH2cg05",
    slot2: "https://buy.stripe.com/4gMcN40sY41Zf5N1aV2cg06",
    slot3: "https://buy.stripe.com/aFa8wO0sY1TRbTB1aV2cg07"
  },
  slots: {
    slot1: {
      code: "SLOT 01",
      title: "Pack Pilotage Micro & TPE 2027",
      priceEur: 19,
      reference: "FK27-S01-PILOTAGE",
      summary: "Classeur Excel automatisé 5 onglets (seuils TVA art. 293 B, URSSAF, Livre des recettes normé 2026-2027, Comparateur Plateformes Agréées, Simulateur TJM) + Guide PDF pratique."
    },
    slot2: {
      code: "SLOT 02",
      title: "Studio Factur-X Local 2027",
      priceEur: 49,
      reference: "FK27-S02-STUDIO",
      summary: "Application Web 100% locale sans abonnement (générateur Devis & Factures PDF/Factur-X hybrides EN 16931, validation SIREN Luhn, inspecteur Factur-X fournisseur) + CLI Python & Guide."
    },
    slot3: {
      code: "SLOT 03",
      title: "Suite Opérations & Automatisation TPE 2027 (Édition Pro)",
      priceEur: 119,
      reference: "FK27-S03-SUITEPRO",
      summary: "Pack Complet Tout-en-un : inclut intégralement les Slots 01 & 02 + 3 Workflows n8n/Make prêts à importer + Kit Conformité EU AI Act & RGPD PME."
    }
  }
};
