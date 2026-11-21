#!/usr/bin/env python3
"""Deterministic Programmatic SEO generator for FacturKit 2027.

Generates:
  - metiers/index.html (searchable & sector-filterable directory of 50 French professions)
  - metiers/<slug>.html (50 distinct NAF/profession Factur-X 2026-2027 compliance pages)
  - Updates sitemap.xml cleanly with all existing + new URLs (64 URLs total)

Zero external dependencies (Python 3 stdlib only). Zero PII/DEC-2.
"""

from __future__ import annotations

import html
import json
from pathlib import Path

SITE_BASE = "https://yannabadie.github.io/facturkit-2027"
LASTMOD = "2026-11-21"

STRIPE_SLOT1 = "https://buy.stripe.com/3cIaEWfnS8ifbTBdXH2cg05"
STRIPE_SLOT2 = "https://buy.stripe.com/4gMcN40sY41Zf5N1aV2cg06"
STRIPE_SLOT3 = "https://buy.stripe.com/aFa8wO0sY1TRbTB1aV2cg07"
GUMROAD_HFXUUZ = "https://yannabadi.gumroad.com/l/hfxuuz"

PA_INFO = {
    "indy": ("Indy", "affilae-indy", "https://www.indy.fr/", "PA immatriculée DGFiP (09/01/2026)", "Facturation 0 € · Compta dès 16 €/m"),
    "tiime": ("Tiime", "affilae-tiime", "https://www.tiime.fr/", "PA immatriculée DGFiP (18/12/2025)", "Factur-X 0 € · Compte pro dès 9,99 €/m"),
    "pennylane": ("Pennylane", "affilae-pennylane", "https://www.pennylane.com/fr/", "PA immatriculée DGFiP (11/12/2025)", "Socle micro 0 € · PME & cabinets"),
    "qonto": ("Qonto", "affilae-qonto", "https://qonto.com/fr", "PA immatriculée DGFiP (18/12/2025)", "Compte pro + PA dès 9 € HT/m"),
    "shine": ("Shine", "affilae-shine", "https://www.shine.fr/", "Compte pro + Shine Facture", "Offre Free 0 € · Pro dès 11 € HT/m"),
    "abby": ("Abby", "affilae-abby", "https://www.abby.gg/", "Micro-entreprise & Factur-X", "Plan gratuit · Pro dès 10 €/m"),
    "axonaut": ("Axonaut", "direct-axonaut", "https://axonaut.com/", "PA immatriculée DGFiP (08/01/2026)", "CRM + PA TPE/PME dès 49 €/m"),
    "sellsy": ("Sellsy", "direct-sellsy", "https://go.sellsy.com/", "PA immatriculée DGFiP (24/12/2025)", "CRM + Facturation PME dès 39 €/u/m"),
}

# 50 real French professions with authentic NAF codes, legal/TVA edge cases, and recommended PAs
PROFESSIONS = [
    # --- Tech, Conseil & Finance (10) ---
    {
        "slug": "expert-comptable",
        "title": "Expert-comptable & Cabinet comptable",
        "short": "Expert-comptable",
        "naf": "69.20Z",
        "sector": "Conseil & Finance",
        "flux": "B2B (e-invoicing) + multi-mandats clients",
        "tva": "Assujetti TVA 20 % (honoraires, lettres de mission récurrentes)",
        "edge_cases": [
            "Pilotage simultané de la réception obligatoire (en vigueur depuis le 01/09/2026) pour l'ensemble du portefeuille clients TPE/PME.",
            "Contrôle rapide des factures fournisseurs Factur-X 1.09.2 / ZUGFeRD 2.5.2 et des 4 statuts de cycle de vie CDAR (Déposée, Prise en charge, Refusée, Encaissée).",
            "Interconnexion cabinet multi-PA via l'annuaire central (159 PA immatriculées DGFiP) sans enfermer les TPE clientes dans un seul outil payant.",
        ],
        "checklist": [
            "Auditer 100 % des clients TPE/micro du cabinet n'ayant pas encore choisi leur PA de réception.",
            "Standardiser la vérification locale des fichiers PDF/A-3 Factur-X avant intégration comptable (export CSV batch).",
            "Paramétrer l'option « TVA sur les débits » ou « sur les encaissements » dans les métadonnées XML EN 16931.",
        ],
        "pas": ["pennylane", "tiime", "sellsy"],
        "faq_q": "Un cabinet comptable peut-il inspecter les Factur-X clients hors-ligne avant import ?",
        "faq_a": "Oui. En complément de votre PA (Pennylane, Tiime ou logiciel cabinet), un inspecteur local PDF/A-3 EN 16931 comme FacturKit ou la CLI open-source facturx-france-2027 permet d'auditer des lots de factures sans transférer de pièces clients vers un tiers.",
    },
    {
        "slug": "developpeur-freelance",
        "title": "Développeur freelance & Ingénieur logiciel",
        "short": "Développeur freelance",
        "naf": "62.01Z",
        "sector": "Tech & Digital",
        "flux": "B2B France (e-invoicing) + Clients UE/US (e-reporting international)",
        "tva": "Franchise art. 293 B ou TVA 20 % / Autoliquidation intracommunautaire (art. 283-2 CGI)",
        "edge_cases": [
            "Prestations facturées à des clients étrangers (UE avec numéro de TVA intracommunautaire ou hors UE US/UK) : bascule en e-reporting de transactions internationales.",
            "Suivi strict du seuil de franchise en base de TVA (prestations de services) et mention obligatoire « TVA non applicable, art. 293 B du CGI » dans le bloc XML BT-120.",
            "Facturation au TJM avec CRA mensuel joint : obligation d'inclure le SIREN client et la catégorie « Prestation de services ».",
        ],
        "checklist": [
            "Activer immédiatement une PA de réception gratuite (Tiime ou Indy) pour éviter l'amende de 500 € -> 1 000 €/trim. (LFI 2026 art. 123).",
            "Vérifier le numéro de TVA intracommunautaire (VIES) de chaque client UE avant émission.",
            "Simuler l'arbitrage Micro-entreprise BNC (25,8 % URSSAF 2026) vs EURL/SASU dès 50 000 € de CA.",
        ],
        "pas": ["indy", "tiime", "qonto"],
        "faq_q": "Un développeur freelance en micro-entreprise qui facture aux États-Unis doit-il avoir une PA ?",
        "faq_a": "Oui. La réception électronique est obligatoire depuis le 1er septembre 2026 pour recevoir vos factures fournisseurs français (télécom, matériel, coworking), et vos ventes hors France relèvent de l'e-reporting international à compter du 1er septembre 2027.",
    },
    {
        "slug": "consultant-it",
        "title": "Consultant IT, Cybersécurité & Cloud",
        "short": "Consultant IT",
        "naf": "62.02A",
        "sector": "Tech & Digital",
        "flux": "B2B grands comptes / ESN (e-invoicing) + Secteur public (Chorus Pro)",
        "tva": "TVA 20 % sur encaissements (option débits possible)",
        "edge_cases": [
            "Sous-traitance via ESN ou plateformes de portage/intermédiation : bien distinguer l'adresse de facturation (SIREN ESN) et la référence bon de commande (BT-13) exigée par les grands comptes.",
            "Missions secteur public : passage obligatoire par Chorus Pro (code service + numéro d'engagement juridique).",
            "Encaissements à 45 ou 60 jours fin de mois : transmission du statut « Encaissée » (e-reporting de paiement) indispensable si TVA sur les encaissements.",
        ],
        "checklist": [
            "Vérifier les 4 mentions 2026–2027 (SIREN client, catégorie de l'opération, adresse de livraison, option TVA débits).",
            "Connecter votre compte pro / PA pour automatiser le rapprochement et le statut d'encaissement.",
            "Archiver les PDF/A-3 hybrides 10 ans en conformité fiscale.",
        ],
        "pas": ["qonto", "pennylane", "indy"],
        "faq_q": "Les grandes entreprises clientes exigent-elles déjà le format Factur-X dès fin 2026 ?",
        "faq_a": "Les grandes entreprises et ETI émettent en facturation électronique depuis le 1er septembre 2026 ; elles acceptent vos factures classiques jusqu'au 1er septembre 2027 mais beaucoup encouragent dès maintenant l'envoi Factur-X pour accélérer le règlement.",
    },
    {
        "slug": "agence-web",
        "title": "Agence web, Studio digital & ESN TPE",
        "short": "Agence web",
        "naf": "62.01Z",
        "sector": "Tech & Digital",
        "flux": "B2B France (e-invoicing) + Abonnements maintenance récurrents + Export",
        "tva": "TVA 20 % (acomptes 30–50 %, soldes, hébergement annuel)",
        "edge_cases": [
            "Factures d'acompte (type code 386 en EN 16931) et factures de solde déduisant les acomptes versés : source fréquente de rejet BR-CO sur les totaux XML.",
            "Refacturation de noms de domaine, licences SaaS ou budgets pub : distinguer débours véritables (au nom du client) et refacturation soumise à TVA.",
            "Gestion des avoirs (type code 381) liés à un numéro de facture initiale obligatoire.",
        ],
        "checklist": [
            "Tester vos factures d'acompte et d'avoir avec un validateur EN 16931 (règles BR-CO-10 à BR-CO-16).",
            "Choisir un outil CRM + PA native (Axonaut, Sellsy ou Pennylane) pour lier devis signés et factures Factur-X.",
            "Mettre à jour vos CGV et modèles de devis avec les mentions 2026–2027.",
        ],
        "pas": ["axonaut", "pennylane", "sellsy"],
        "faq_q": "Comment gérer les factures d'acompte d'une agence web en Factur-X ?",
        "faq_a": "En norme EN 16931 (Factur-X 1.09.2), chaque acompte encaissé impose une facture électronique dédiée (code 386) puis une déduction explicite dans le champ BT-113 (montant payé d'avance) de la facture de solde.",
    },
    {
        "slug": "data-scientist-ia",
        "title": "Data Scientist, Consultant IA & Automatisation",
        "short": "Consultant IA & Data",
        "naf": "62.02A",
        "sector": "Tech & Digital",
        "flux": "B2B France + Export UE/US + Prestations SaaS/API",
        "tva": "TVA 20 % ou autoliquidation B2B UE / Hors champ art. 259-1 CGI hors UE",
        "edge_cases": [
            "Double contrainte réglementaire depuis août–septembre 2026 : réception Factur-X obligatoire ET transparence EU AI Act Art. 50 (Règlement Digital Omnibus (UE) 2026/1744).",
            "Facturation de licences logicielles ou d'accès API à l'étranger : ventilation précise entre e-invoicing domestique et e-reporting international.",
            "Achat de crédits cloud/LLM auprès d'éditeurs américains (autoliquidation TVA intracommunautaire ou hors UE à déclarer sur CA3).",
        ],
        "checklist": [
            "Déclarer une PA de réception gratuite dès maintenant pour vos factures fournisseurs français.",
            "Séparer clairement prestations de conseil, licences logicielles et frais cloud dans vos lignes de facturation.",
            "Préparer vos modèles Factur-X EN 16931 et votre registre Art. 50 AI Act dans un même cockpit.",
        ],
        "pas": ["qonto", "indy", "pennylane"],
        "faq_q": "Les factures cloud US (OpenAI, Anthropic, AWS) passent-elles par ma Plateforme Agréée ?",
        "faq_a": "Les fournisseurs établis hors de France ne transitent pas par le réseau e-invoicing domestique, mais ces achats B2B internationaux entrent dans votre e-reporting d'acquisitions (autoliquidation de TVA).",
    },
    {
        "slug": "consultant-strategie-gestion",
        "title": "Consultant en stratégie, management & organisation",
        "short": "Consultant gestion",
        "naf": "70.22Z",
        "sector": "Conseil & Finance",
        "flux": "B2B PME/ETI/Grands comptes (e-invoicing)",
        "tva": "TVA 20 % sur encaissements (ou franchise 293 B en démarrage)",
        "edge_cases": [
            "Refacturation des frais de déplacement (train, hôtel, indemnités kilométriques) : les frais refacturés suivent le régime TVA de la prestation principale (20 %).",
            "Contrats au forfait + variable (success fee) : facturation échelonnée et suivi rigoureux des statuts de paiement.",
            "Exigences d'achat des ETI/grands groupes (numéro PO / bon de commande obligatoire dans BT-13 sous peine de rejet).",
        ],
        "checklist": [
            "Enregistrer votre SIREN sur l'annuaire central via une PA immatriculée DGFiP.",
            "Intégrer systématiquement le champ « Numéro de bon de commande » et « SIREN client » dans vos factures.",
            "Comparer EI réel, EURL et SASU selon votre taux de charges et frais professionnels.",
        ],
        "pas": ["indy", "qonto", "pennylane"],
        "faq_q": "Dois-je facturer la TVA sur les billets de train refacturés à mon client ?",
        "faq_a": "Oui, sauf convention expresse de débours au nom et pour le compte du client (facture établie directement au nom du client). En refacturation classique, les frais de mission intègrent la base taxable à 20 %.",
    },
    # --- BTP, Construction & Artisanat (7) ---
    {
        "slug": "artisan-batiment-macon",
        "title": "Artisan du bâtiment & Maçonnerie générale",
        "short": "Artisan bâtiment",
        "naf": "43.99C",
        "sector": "BTP & Artisanat",
        "flux": "Mixte B2B (sous-traitance, promoteurs) + B2C particuliers (e-reporting)",
        "tva": "Multi-taux (20 %, 10 % rénovation, 5,5 % énergétique) + Autoliquidation BTP (art. 283-2 nonies)",
        "edge_cases": [
            "Autoliquidation de TVA en sous-traitance BTP (art. 283-2 nonies du CGI) : facture émise HT avec code catégorie TVA AE (« Reverse charge ») et mention obligatoire « Autoliquidation ».",
            "Factures de situations de travaux (avancement cumulé) et retenues de garantie 5 % : calcul précis du net à payer en EN 16931.",
            "Chantiers chez des particuliers (B2C) : hors e-invoicing mais soumis à l'e-reporting de transactions B2C à partir du 01/09/2027.",
        ],
        "checklist": [
            "Choisir une PA de réception dès aujourd'hui pour recevoir les factures de vos négociants matériaux (Point.P, Rexel, etc. émettent déjà en e-invoicing !).",
            "Vérifier l'adresse du chantier distincte de l'adresse de facturation (mention adresse de livraison obligatoire).",
            "Préparer vos taux de TVA multiples (5,5 % / 10 % / 20 %) et la mention « Livraison de biens et prestations de services » (opération mixte).",
        ],
        "pas": ["axonaut", "tiime", "shine"],
        "faq_q": "Mes fournisseurs de matériaux m'envoient déjà des factures électroniques en 2026 ?",
        "faq_a": "Oui ! Les grands négoces BTP (ETI et grandes entreprises) ont basculé en émission obligatoire le 1er septembre 2026. Vous devez disposer d'une PA immatriculée pour recevoir et archiver leurs factures.",
    },
    {
        "slug": "plombier-chauffagiste",
        "title": "Plombier, Chauffagiste & Installateur thermique (RGE)",
        "short": "Plombier-chauffagiste",
        "naf": "43.22A",
        "sector": "BTP & Artisanat",
        "flux": "B2C dépannage/rénovation (e-reporting) + B2B syndics/entreprises (e-invoicing)",
        "tva": "TVA 5,5 % (rénovation énergétique PAC/chaudière), 10 % (logement > 2 ans), 20 % (neuf/pro)",
        "edge_cases": [
            "Opérations mixtes matériel + main-d'œuvre : la mention légale « Livraison de biens et prestations de services » est obligatoire sur chaque facture.",
            "Dossiers MaPrimeRénov' / CEE (artisans RGE) : ventilation exacte des équipements éligibles TVA 5,5 % et mention de l'adresse d'intervention.",
            "Facturation aux syndics de copropriété et bailleurs sociaux : SIREN du syndicat ou du bailleur requis et format Factur-X exigé.",
        ],
        "checklist": [
            "Activer votre PA de réception pour les grossistes sanitaires/chauffage (Cedeo, Brossette, etc.).",
            "Indiquer systématiquement l'adresse du lieu d'intervention si différente de l'adresse de facturation.",
            "Séparer fournitures et main-d'œuvre avec leurs taux de TVA respectifs dans le XML Factur-X.",
        ],
        "pas": ["tiime", "axonaut", "shine"],
        "faq_q": "Une facture de dépannage plomberie chez un particulier doit-elle être envoyée en Factur-X ?",
        "faq_a": "Non, les factures aux particuliers (B2C) ne transitent pas en e-invoicing, mais leurs données de chiffre d'affaires et de TVA devront être transmises via l'e-reporting à compter du 1er septembre 2027.",
    },
    {
        "slug": "electricien",
        "title": "Électricien bâtiment, Domotique & IRVE",
        "short": "Électricien",
        "naf": "43.21A",
        "sector": "BTP & Artisanat",
        "flux": "B2B entreprises/promoteurs (e-invoicing) + B2C particuliers (e-reporting)",
        "tva": "TVA 5,5 % (bornes IRVE/rénovation énergétique), 10 % (rénovation), 20 % + Autoliquidation sous-traitance",
        "edge_cases": [
            "Sous-traitance sur chantiers tertiaires ou industriels : autoliquidation TVA (art. 283-2 nonies) à coder en catégorie AE en Factur-X.",
            "Installation de bornes de recharge IRVE et panneaux solaires : taux réduit 5,5 % sous conditions + adresse d'installation obligatoire.",
            "Réception massive de factures grossistes électriques (Rexel, Sonepar) déjà en format électronique depuis le 01/09/2026.",
        ],
        "checklist": [
            "Désigner immédiatement votre PA sur l'annuaire central pour réceptionner vos factures grossistes.",
            "Paramétrer les 3 taux de TVA (5,5 %, 10 %, 20 %) et le profil autoliquidation dans votre outil.",
            "Contrôler la mention « Opération mixte » sur les factures comprenant câbles/tableaux et pose.",
        ],
        "pas": ["tiime", "axonaut", "qonto"],
        "faq_q": "Que risque un artisan électricien sans Plateforme Agréée fin 2026 ?",
        "faq_a": "L'article 123 de la LFI 2026 prévoit, après mise en demeure de 3 mois restée sans effet, une amende de 500 € puis 1 000 € par trimestre tant qu'aucune PA n'est choisie, en plus des blocages de réception fournisseurs.",
    },
    {
        "slug": "peintre-batiment",
        "title": "Peintre en bâtiment & Revêtements sols/murs",
        "short": "Peintre en bâtiment",
        "naf": "43.34Z",
        "sector": "BTP & Artisanat",
        "flux": "B2C particuliers (e-reporting) + B2B assurances/syndics/entreprises (e-invoicing)",
        "tva": "TVA 10 % (logement > 2 ans), 20 % (locaux pro/neuf) ou Franchise 293 B",
        "edge_cases": [
            "Indemnisations sinistres dégâts des eaux : facturation adressée au client avec délégation de paiement compagnie d'assurance (attention au SIREN du destinataire réel).",
            "Acomptes à la commande (30 % ou 40 %) avant démarrage chantier : factures d'acompte structurées obligatoires en B2B dès 2027.",
            "Achats fréquents en magasin pro (peintures, outillage) : réception électronique déjà active chez les grandes enseignes.",
        ],
        "checklist": [
            "Ouvrir une PA gratuite (Tiime ou Shine/Indy) pour centraliser vos factures fournisseurs.",
            "Vérifier l'attestation simplifiée TVA 10 % et mentionner l'adresse exacte du chantier.",
            "Suivre vos seuils micro-entreprise (77 700 € services / 188 700 € mixte) et franchise TVA.",
        ],
        "pas": ["tiime", "shine", "abby"],
        "faq_q": "Un peintre auto-entrepreneur en franchise de TVA est-il concerné par la réforme 2026 ?",
        "faq_a": "Oui. Toutes les entreprises établies en France, y compris les micro-entrepreneurs en franchise de TVA (art. 293 B), doivent pouvoir recevoir des factures électroniques depuis le 1er septembre 2026.",
    },
    {
        "slug": "menuisier-charpentier",
        "title": "Menuisier, Charpentier & Agenceur",
        "short": "Menuisier-charpentier",
        "naf": "43.32A",
        "sector": "BTP & Artisanat",
        "flux": "B2B constructeurs/architectes (e-invoicing) + B2C particuliers (e-reporting)",
        "tva": "TVA 5,5 % (fenêtres isolantes RGE), 10 % (rénovation), 20 % (neuf/pro) + Autoliquidation BTP",
        "edge_cases": [
            "Fabrication sur mesure + pose : double qualification vente de biens + prestation de services (« opération mixte »).",
            "Acomptes importants à la commande de bois/menuiseries : facturation d'acomptes et retenues de garantie sur marchés privés ou publics (Chorus Pro).",
            "Sous-traitance pour entreprises générales : autoliquidation TVA BTP obligatoire.",
        ],
        "checklist": [
            "Rattacher votre SIREN à une PA immatriculée pour recevoir les factures scieries et quincailleries.",
            "Séparer fourniture sur mesure et main-d'œuvre avec mention des performances thermiques si TVA 5,5 %.",
            "Valider vos modèles de factures de situation et d'acompte au format Factur-X 1.09.2.",
        ],
        "pas": ["axonaut", "tiime", "qonto"],
        "faq_q": "Comment facturer une mairie ou un collège en menuiserie ?",
        "faq_a": "Les factures destinées au secteur public (B2G) continuent de passer par le portail public gratuit Chorus Pro, qui accepte nativement le format Factur-X.",
    },
    {
        "slug": "couvreur-zingueur",
        "title": "Couvreur, Zingueur & Étanchéité toiture",
        "short": "Couvreur-zingueur",
        "naf": "43.91B",
        "sector": "BTP & Artisanat",
        "flux": "B2C particuliers + B2B copropriétés/promoteurs (e-invoicing)",
        "tva": "TVA 5,5 % (isolation toiture RGE), 10 % (réfection > 2 ans), 20 % (neuf/locaux pro)",
        "edge_cases": [
            "Interventions sur copropriétés gérées par syndics : vérification indispensable du SIREN du syndicat des copropriétaires (et non uniquement du cabinet syndic).",
            "Marchés avec assurance décennale mentionnée sur devis et factures (compagnie, numéro de police, zone géographique).",
            "Sous-traitance charpente/couverture : autoliquidation de TVA obligatoire.",
        ],
        "checklist": [
            "Activer votre PA de réception pour vos fournisseurs matériaux de couverture.",
            "Conserver la mention obligatoire d'assurance décennale sur vos PDF/A-3 Factur-X.",
            "Contrôler la mention d'adresse du chantier et le taux de TVA réduit applicable.",
        ],
        "pas": ["tiime", "axonaut", "shine"],
        "faq_q": "La mention d'assurance décennale reste-t-elle obligatoire sur une facture Factur-X ?",
        "faq_a": "Oui. La réforme électronique ajoute 4 mentions fiscales mais ne supprime aucune mention sectorielle obligatoire (assurance décennale BTP, qualification RGE, numéro de police).",
    },
    {
        "slug": "paysagiste",
        "title": "Paysagiste, Entretien d'espaces verts & SAP",
        "short": "Paysagiste",
        "naf": "81.30Z",
        "sector": "BTP & Artisanat",
        "flux": "B2C (petit jardinage SAP / aménagements) + B2B entreprises & collectivités",
        "tva": "TVA 20 % (création & entretien jardinage) · TVA 10 % (certains travaux forestiers/agricoles)",
        "edge_cases": [
            "Prestations de petit jardinage éligibles au crédit d'impôt Services à la Personne (SAP) : facturation spécifique (coopérative ou entité dédiée SAP, paiement non espèces).",
            "Contrats annuels d'entretien d'espaces verts pour entreprises/résidences : facturation mensuelle ou trimestrielle en e-invoicing B2B.",
            "Marchés publics espaces verts (communes) : facturation via Chorus Pro.",
        ],
        "checklist": [
            "Distinguer vos factures B2B (e-invoicing via PA) et vos factures particuliers B2C (e-reporting 2027).",
            "Vérifier l'application du taux de TVA 20 % sur les prestations d'aménagement paysager.",
            "Mettre en place une PA de réception gratuite pour vos achats pépinières et motoculture.",
        ],
        "pas": ["tiime", "shine", "axonaut"],
        "faq_q": "Un paysagiste qui passe par une coopérative SAP doit-il choisir une PA ?",
        "faq_a": "Oui pour son activité propre (création, chantiers B2B et factures fournisseurs reçues depuis le 01/09/2026), même si la coopérative facture les particuliers SAP.",
    },
    # --- Architecture, Ingénierie & Droit (6) ---
    {
        "slug": "architecte",
        "title": "Architecte DPLG / HMONP & Maître d'œuvre",
        "short": "Architecte",
        "naf": "71.11Z",
        "sector": "Architecture & Droit",
        "flux": "B2B promoteurs/entreprises + B2G collectivités (Chorus Pro) + B2C particuliers",
        "tva": "TVA 20 % (10 % uniquement si maîtrise d'œuvre liée à travaux éligibles > 2 ans)",
        "edge_cases": [
            "Notes d'honoraires par phases (ESQ, APS, APD, PRO, EXE, DET, AOR) : suivi des pourcentages d'avancement cumulés dans les factures structurées.",
            "Groupements de maîtrise d'œuvre (cotraitance avec BET) : chaque cotraitant émet sa propre facture électronique (ou via mandataire) avec ventilation précise.",
            "Marchés publics d'architecture : dépôt obligatoire sur Chorus Pro avec numéro de marché.",
        ],
        "checklist": [
            "Choisir une PA adaptée aux honoraires par phases et au suivi de trésorerie (Pennylane, Indy ou Axonaut).",
            "Renseigner l'adresse du projet immobilier dans le champ « Adresse de livraison/exécution ».",
            "Contrôler le taux de TVA (10 % vs 20 %) selon l'ancienneté du bâti et la nature de la mission.",
        ],
        "pas": ["pennylane", "indy", "axonaut"],
        "faq_q": "Une note d'honoraires d'architecte est-elle soumise au format Factur-X ?",
        "faq_a": "Oui. Juridiquement, une note d'honoraires B2B est une facture à part entière : elle suit exactement les mêmes obligations de réception (01/09/2026) et d'émission structurée (01/09/2027).",
    },
    {
        "slug": "bureau-etudes-ingenierie",
        "title": "Bureau d'études techniques (BET) & Ingénierie",
        "short": "Bureau d'études",
        "naf": "71.12B",
        "sector": "Architecture & Droit",
        "flux": "B2B donneurs d'ordre / industrie / BTP + B2G (Chorus Pro)",
        "tva": "TVA 20 % sur encaissements (option débits fréquente en société)",
        "edge_cases": [
            "Facturation par jalons techniques et bons de commande industriels (exigence stricte de référence contrat/PO).",
            "Distinction claire entre études techniques (prestations de services) et fourniture de prototypes/matériels.",
            "Clients industriels ETI/Grands groupes : réception et contrôle strict des rejets de facture.",
        ],
        "checklist": [
            "Vérifier si votre société a opté pour la TVA sur les débits (mention obligatoire sur chaque facture).",
            "Paramétrer votre PA avec un contrôle automatisé du SIREN client et du numéro de commande.",
            "Utiliser un validateur Factur-X local avant dépôt pour éviter les rejets techniques (50 €/facture max art. 1737 III).",
        ],
        "pas": ["pennylane", "sellsy", "qonto"],
        "faq_q": "Comment éviter les rejets de factures chez les grands donneurs d'ordre industriels ?",
        "faq_a": "En vérifiant systématiquement avant envoi la conformité EN 16931 (règles BR-CO), le SIREN exact du client, la référence de commande BT-13 et le code routage de sa Plateforme Agréée.",
    },
    {
        "slug": "geometre-expert",
        "title": "Géomètre-expert & Topographe",
        "short": "Géomètre-expert",
        "naf": "71.12A",
        "sector": "Architecture & Droit",
        "flux": "B2B promoteurs/notaires/aménageurs + B2G collectivités + B2C bornages",
        "tva": "TVA 20 % (prestations d'expertise, bornages, copropriétés)",
        "edge_cases": [
            "Facturation mixte : missions de bornage pour particuliers (e-reporting B2C) et divisions foncières pour promoteurs/collectivités (e-invoicing B2B / Chorus Pro).",
            "Frais de publication foncière ou taxes avancées pour le compte du client (régime strict des débours art. 267 II 2° CGI).",
            "Numéro d'inscription à l'Ordre des Géomètres-Experts à conserver sur les documents PDF/A-3.",
        ],
        "checklist": [
            "Mettre en place votre PA de réception pour l'équipement topographique et les logiciels CAO.",
            "Séparer nettement honoraires taxables et débours non soumis à TVA dans vos écritures.",
            "Préparer le flux e-reporting B2C pour les particuliers (échéance 01/09/2027).",
        ],
        "pas": ["pennylane", "indy", "qonto"],
        "faq_q": "Les débours avancés par un géomètre doivent-ils figurer dans le XML Factur-X ?",
        "faq_a": "S'ils sont présentés sur la même facture, les débours stricts (facturés au nom du client) sont identifiés hors base TVA (catégorie O / Hors champ) afin de ne pas fausser la déclaration CA3.",
    },
    {
        "slug": "avocat",
        "title": "Avocat & Cabinet d'avocats",
        "short": "Avocat",
        "naf": "69.10Z",
        "sector": "Architecture & Droit",
        "flux": "B2B entreprises (e-invoicing) + B2C particuliers (e-reporting) + Aide juridictionnelle (B2G)",
        "tva": "TVA 20 % sur encaissements (provisions, honoraires au temps passé ou résultat) + Débours",
        "edge_cases": [
            "Secret professionnel : les libellés de lignes transmis à la Plateforme Agréée et à l'administration doivent rester génériques (« Honoraires de conseil juridique — Dossier n°… ») sans exposer de données confidentielles clients.",
            "Appels de provisions sur honoraires : assimilés à des acomptes imposant une facture structurée et un suivi de TVA sur encaissements.",
            "Frais de greffe, timbres fiscaux, droits de plaidoirie : distinction stricte entre débours exonérés et frais refacturés.",
        ],
        "checklist": [
            "Vérifier la compatibilité PA / secret professionnel (hébergement SecNumCloud / ISO 27001) de votre outil.",
            "Standardiser des libellés d'honoraires conformes au secret professionnel sur vos modèles Factur-X.",
            "Automatiser le suivi des provisions et des encaissements pour la TVA sur encaissements.",
        ],
        "pas": ["indy", "pennylane", "qonto"],
        "faq_q": "La facturation électronique remet-elle en cause le secret professionnel de l'avocat ?",
        "faq_a": "Non, à condition d'utiliser des libellés de prestations neutres (sans nom de partie adverse ni détail stratégique) et de choisir une PA immatriculée soumise aux exigences strictes de sécurité ISO 27001 / SecNumCloud.",
    },
    {
        "slug": "notaire",
        "title": "Étude notariale & Notaire",
        "short": "Notaire",
        "naf": "69.10Z",
        "sector": "Architecture & Droit",
        "flux": "Réception fournisseurs B2B (LIVE 2026) + Actes B2B/B2C & débours publics",
        "tva": "TVA 20 % sur émoluments/honoraires · Débours publics & droits d'enregistrement hors TVA",
        "edge_cases": [
            "Forte volumétrie de factures fournisseurs (informatique notariale, prestataires, locaux) : réception électronique active depuis le 01/09/2026.",
            "Distinction rigoureuse entre émoluments taxables à 20 %, honoraires libres et droits/taxes perçus pour le Trésor Public.",
            "Facturation aux sociétés (acquisitions immobilières, baux commerciaux) soumise au format structuré B2B dès 2027.",
        ],
        "checklist": [
            "Connecter l'étude à une PA immatriculée interopérable avec votre comptabilité notariale.",
            "Auditer la conformité des mentions 2026–2027 sur vos factures d'honoraires sociétés.",
            "Mettre en place un contrôle local PDF/A-3 pour les factures fournisseurs entrantes.",
        ],
        "pas": ["pennylane", "sellsy", "qonto"],
        "faq_q": "Une étude notariale doit-elle déjà avoir choisi une PA en novembre 2026 ?",
        "faq_a": "Oui. En tant qu'assujettie établie en France, l'étude doit être en mesure de recevoir les factures électroniques de ses fournisseurs depuis le 1er septembre 2026.",
    },
    {
        "slug": "commissaire-justice",
        "title": "Commissaire de justice (ex-Huissier / Commissaire-priseur)",
        "short": "Commissaire de justice",
        "naf": "69.10Z",
        "sector": "Architecture & Droit",
        "flux": "B2B créanciers/entreprises (e-invoicing) + B2C particuliers (e-reporting)",
        "tva": "TVA 20 % sur actes et constats + Débours réglementés hors TVA",
        "edge_cases": [
            "Ventilation complexe entre émoluments réglementés, frais de déplacement (SCT), honoraires de constat et débours/taxes.",
            "Facturation fréquente à des sociétés créancières, bailleurs institutionnels et cabinets d'avocats (flux B2B e-invoicing).",
            "Contrôle strict des statuts d'encaissement pour la TVA exigible à l'encaissement.",
        ],
        "checklist": [
            "Activer votre PA de réception dès maintenant pour tous les fournisseurs de l'office.",
            "Vérifier le mapping des lignes débours vs honoraires taxables dans vos exports comptables.",
            "Former l'équipe au contrôle des factures Factur-X entrantes.",
        ],
        "pas": ["pennylane", "qonto", "tiime"],
        "faq_q": "Les constats facturés à des entreprises relèvent-ils de l'e-invoicing ?",
        "faq_a": "Oui. Toute prestation de constat ou de recouvrement facturée à une entreprise assujettie établie en France entre dans le champ de la facturation électronique B2B (émission au 01/09/2027 pour les TPE/PME).",
    },
    # --- Santé, Médical & Paramédical (8) ---
    {
        "slug": "medecin-liberal",
        "title": "Médecin libéral (Généraliste & Spécialiste)",
        "short": "Médecin libéral",
        "naf": "86.21Z",
        "sector": "Santé & Libéral",
        "flux": "Actes de soins exonérés (hors e-invoicing/e-reporting) · Réception fournisseurs OBLIGATOIRE 2026",
        "tva": "Exonération TVA soins médicaux (art. 261-4-1° CGI) · TVA 20 % sur expertises/esthétique",
        "edge_cases": [
            "Point clé méconnu : même si vos actes médicaux exonérés (art. 261-4-1° CGI) sont hors champ d'émission, votre cabinet DOIT disposer d'une PA de réception (fournisseurs matériel médical, logiciels, laboratoire, télécom) si vous êtes assujetti (ex. actes non exonérés, rétrocessions ou SCM).",
            "Actes hors soins (médecine esthétique pure, expertises assurances/tribunaux, conférences laboratoires) : soumis à TVA 20 % et au e-invoicing/e-reporting !",
            "SCM / SISA : la société de moyens qui reçoit les factures communes doit impérativement être inscrite sur une PA.",
        ],
        "checklist": [
            "Vérifier si vous réalisez des actes annexes taxables (expertises, conférences, esthétique) ou appartenez à une SCM.",
            "Ouvrir une PA gratuite (Indy ou Tiime) pour recevoir sereinement toutes vos factures fournisseurs.",
            "Séparer comptablement les recettes exonérées art. 261-4-1° et les honoraires soumis à TVA.",
        ],
        "pas": ["indy", "tiime", "shine"],
        "faq_q": "Un médecin libéral 100 % exonéré de TVA doit-il quand même s'intéresser à la réforme 2026 ?",
        "faq_a": "Oui pour la réception des factures de ses fournisseurs français (et impérativement s'il fait partie d'une SCM ou réalise ne serait-ce qu'un acte non exonéré comme une expertise ou une intervention rémunérée par un laboratoire).",
    },
    {
        "slug": "infirmier-liberal",
        "title": "Infirmier libéral (IDEL) & Cabinet infirmier",
        "short": "Infirmier libéral",
        "naf": "86.90D",
        "sector": "Santé & Libéral",
        "flux": "Soins patients exonérés (SESAM-Vitale) · Réception factures fournisseurs/SCM",
        "tva": "Exonéré de TVA sur les soins (art. 261-4-1° CGI)",
        "edge_cases": [
            "Les télétransmissions SESAM-Vitale / CPAM pour actes de soins exonérés ne passent pas en Factur-X.",
            "En revanche, les achats professionnels (consommables médicaux, logiciel de télétransmission, leasing véhicule, loyer SCM) arrivent au format électronique dès 2026.",
            "En cas de vacations en établissement ou de rétrocessions d'honoraires, vérifiez votre statut d'assujetti partiel.",
        ],
        "checklist": [
            "Identifier si votre cabinet/SCM a désigné une PA de réception gratuite (Indy est très utilisé en BNC santé).",
            "Conserver un suivi mensuel simple des frais professionnels et cotisations URSSAF/CARPIMKO.",
            "Vérifier l'absence de prestations annexes hors soins (formation, coaching) soumises à TVA.",
        ],
        "pas": ["indy", "tiime", "shine"],
        "faq_q": "Les feuilles de soins électroniques (FSE) sont-elles remplacées par Factur-X ?",
        "faq_a": "Non. Les soins dispensés aux patients exonérés de TVA au titre de l'article 261-4-1° du CGI restent gérés via SESAM-Vitale et sont exclus de l'émission Factur-X.",
    },
    {
        "slug": "kinesitherapeute",
        "title": "Masseur-kinésithérapeute libéral",
        "short": "Kinésithérapeute",
        "naf": "86.90E",
        "sector": "Santé & Libéral",
        "flux": "Soins exonérés (hors champ) + Activités bien-être/sport (taxables -> e-reporting/e-invoicing)",
        "tva": "Exonéré art. 261-4-1° (soins) · TVA 20 % sur bien-être / coaching / vente de matériel",
        "edge_cases": [
            "Activités mixtes fréquentes : dès que vous vendez des séances bien-être hors prescription, du Pilates ou du matériel (tapes, coussins), vous devenez assujetti redevable/franchisé sur cette part -> PA obligatoire.",
            "SCM de kinésithérapeutes : réception obligatoire des factures d'équipement (tables, ondes de choc, énergie) via une PA.",
            "Tenue comptable BNC (déclaration 2035) facilitée par une solution santé intégrée.",
        ],
        "checklist": [
            "Séparer strictement les recettes de soins exonérés et les ventes/prestations bien-être soumises à e-reporting.",
            "Désigner une PA gratuite pour la SCM ou votre cabinet individuel.",
            "Vérifier le seuil de franchise TVA sur vos activités annexes hors soins.",
        ],
        "pas": ["indy", "tiime", "abby"],
        "faq_q": "Un kinésithérapeute proposant du Pilates hors nomenclature est-il soumis à Factur-X ?",
        "faq_a": "Oui pour cette activité commerciale/bien-être hors soins exonérés : elle entre dans le périmètre de la réforme (réception 2026 + e-reporting B2C ou e-invoicing B2B en 2027).",
    },
    {
        "slug": "osteopathe",
        "title": "Ostéopathe D.O. & Chiropracteur",
        "short": "Ostéopathe",
        "naf": "86.90F",
        "sector": "Santé & Libéral",
        "flux": "Consultations patients (exonérées) + Interventions en entreprise B2B",
        "tva": "Exonéré art. 261-4-1° CGI (si titre reconnu) · Attention aux ateliers bien-être en entreprise",
        "edge_cases": [
            "Les consultations d'ostéopathie réalisées par un praticien titulaire du diplôme agréé sont exonérées de TVA (art. 261-4-1° CGI), mais les ateliers ergonomie/QVT en entreprise peuvent être taxables -> facturation électronique B2B.",
            "Réception des factures fournisseurs du cabinet (Doctolib, loyers, matériel, assurance RCP).",
            "Contrôle rigoureux du passage micro-BNC -> déclaration contrôlée 2035 dès que les charges dépassent 34 %.",
        ],
        "checklist": [
            "Activer une PA gratuite (Indy ou Tiime) pour la réception fournisseurs et d'éventuelles factures B2B QVT.",
            "Mentionner votre numéro ADELI / RPPS sur vos notes d'honoraires patients.",
            "Simuler Micro-BNC vs EI Réel 2035 avec notre simulateur URSSAF 2026.",
        ],
        "pas": ["indy", "tiime", "abby"],
        "faq_q": "Un ostéopathe intervenant en entreprise pour la QVT doit-il émettre en Factur-X ?",
        "faq_a": "Si la prestation relève du conseil ergonomique ou bien-être (non exonéré art. 261-4-1°), elle relève du B2B domestique soumis à émission électronique au 1er septembre 2027.",
    },
    {
        "slug": "dentiste",
        "title": "Chirurgien-dentiste & Cabinet dentaire (SELARL)",
        "short": "Chirurgien-dentiste",
        "naf": "86.23Z",
        "sector": "Santé & Libéral",
        "flux": "Soins exonérés · Réception laboratoire prothèses & fournisseurs OBLIGATOIRE",
        "tva": "Exonéré soins art. 261-4-1° · Achats prothèses/consommables/équipements lourds en e-invoicing",
        "edge_cases": [
            "Volumes importants de factures fournisseurs (prothésistes dentaires, consommables, imagerie 3D, maintenance) : réception structurée via PA indispensable en SELARL/SCM.",
            "Actes à visée purement esthétique (blanchiment non thérapeutique) : potentiellement taxables et soumis à e-reporting.",
            "Rapprochement des factures de laboratoires prothésistes facilité par l'extraction automatique XML Factur-X.",
        ],
        "checklist": [
            "Relier la SELARL ou la SCM à une PA immatriculée interopérable avec votre expert-comptable.",
            "Contrôler les factures de fournisseurs et prothésistes en format PDF/A-3 structuré.",
            "Distinguer comptablement actes thérapeutiques exonérés et actes esthétiques.",
        ],
        "pas": ["pennylane", "indy", "qonto"],
        "faq_q": "Les factures des prothésistes dentaires arrivent-elles via une Plateforme Agréée ?",
        "faq_a": "Les laboratoires de prothèses (grandes structures dès 2026, PME/TPE au 01/09/2027) émettent leurs factures B2B via leur PA : disposer d'une PA de réception simplifie le contrôle et la comptabilisation.",
    },
    {
        "slug": "pharmacien",
        "title": "Pharmacie d'officine & Parapharmacie",
        "short": "Pharmacien",
        "naf": "47.73Z",
        "sector": "Santé & Libéral",
        "flux": "B2C comptoir multi-taux (e-reporting) + Réception grossistes-répartiteurs B2B (LIVE 2026)",
        "tva": "4 taux simultanés (2,1 % médicaments remboursés, 5,5 %, 10 %, 20 % parapharmacie)",
        "edge_cases": [
            "Réception massive de factures grossistes-répartiteurs (CERP, OCP, Alliance Healthcare) et laboratoires : tous déjà en émission électronique depuis le 01/09/2026 !",
            "Caisse LGO (Logiciel de Gestion d'Officine) : e-reporting quotidien des ventes B2C ventilées sur 4 taux de TVA (2,1 %, 5,5 %, 10 %, 20 %) à préparer pour 2027.",
            "Facturation aux EHPAD et cliniques (B2B) : émission en Factur-X obligatoire au 01/09/2027.",
        ],
        "checklist": [
            "Confirmer le raccordement PA de votre LGO et de votre expert-comptable pour la réception des répartiteurs.",
            "Vérifier la ventilation des 4 taux de TVA dans vos journaux Z de caisse.",
            "Tester la conformité EN 16931 des factures adressées aux EHPAD ou entreprises.",
        ],
        "pas": ["pennylane", "qonto", "sellsy"],
        "faq_q": "Les ventes au comptoir remboursées Sécurité sociale passent-elles en e-reporting ?",
        "faq_a": "Les ventes B2C de médicaments et parapharmacie entrent dans le flux d'e-reporting journalier (transmission agrégée du Z de caisse ventilé par taux de TVA via votre PA à partir du 1er septembre 2027).",
    },
    {
        "slug": "psychologue",
        "title": "Psychologue, Psychothérapeute & Praticien bien-être",
        "short": "Psychologue",
        "naf": "86.90F",
        "sector": "Santé & Libéral",
        "flux": "Consultations patients + Interventions B2B entreprises / cellules RPS",
        "tva": "Exonération art. 261-4-1° (psychologue diplômé d'État) · TVA 20 % ou franchise 293 B pour ateliers/coaching",
        "edge_cases": [
            "Distinction fiscale critique entre soins psychologiques exonérés (diplôme reconnu) et prestations de conseil RPS/formation/coaching en entreprise (assujetties -> e-invoicing B2B).",
            "Obligation de réception électronique pour toutes les factures professionnelles si vous êtes assujetti même en franchise 293 B.",
            "Respect strict du secret médical/professionnel dans les libellés de factures B2B.",
        ],
        "checklist": [
            "Vérifier votre régime TVA exact selon votre diplôme et vos interventions en entreprise.",
            "Activer une PA gratuite (Indy ou Tiime) pour centraliser vos dépenses pro et factures B2B.",
            "Mentionner la base légale d'exonération exacte (art. 261-4-1° ou art. 293 B) sur vos factures.",
        ],
        "pas": ["indy", "tiime", "abby"],
        "faq_q": "Un psychologue qui anime des ateliers prévention RPS en entreprise doit-il émettre des Factur-X ?",
        "faq_a": "Oui. Les prestations facturées à des entreprises (ateliers QVT, audits RPS, formations non exonérées) relèvent du B2B français et basculeront en émission électronique le 1er septembre 2027.",
    },
    {
        "slug": "veterinaire",
        "title": "Vétérinaire & Clinique vétérinaire",
        "short": "Vétérinaire",
        "naf": "75.00Z",
        "sector": "Santé & Libéral",
        "flux": "B2C propriétaires d'animaux (e-reporting) + B2B éleveurs/centres équestres (e-invoicing)",
        "tva": "TVA 20 % (actes vétérinaires, médicaments et aliments — PAS d'exonération médicale !)",
        "edge_cases": [
            "Contrairement aux médecins humains, les vétérinaires sont intégralement assujettis à la TVA à 20 % (actes et ventes) -> 100 % concernés par la réception 2026 et l'émission/e-reporting 2027.",
            "Double flux : facturation B2B structurée pour les éleveurs agricoles, haras et refuges assujettis, et e-reporting B2C pour les particuliers.",
            "Réception électronique immédiate des centrales d'achat vétérinaires (Coveto, Centravet, Alcyon).",
        ],
        "checklist": [
            "Connecter la clinique à une PA immatriculée pour les factures des centrales vétérinaires.",
            "Identifier les clients professionnels (SIREN éleveurs/agriculteurs) dans votre logiciel clinique.",
            "Préparer l'export e-reporting quotidien de la caisse comptoir pour septembre 2027.",
        ],
        "pas": ["pennylane", "qonto", "axonaut"],
        "faq_q": "Les cliniques vétérinaires sont-elles exonérées comme les médecins ?",
        "faq_a": "Non ! Les soins vétérinaires sont soumis à la TVA à 20 %. Les cliniques vétérinaires sont pleinement dans le champ de la réception obligatoire (2026), de l'e-invoicing B2B et de l'e-reporting B2C (2027).",
    },
    # --- Commerce, E-commerce, Restauration & Services B2C (8) ---
    {
        "slug": "e-commerce-vente-en-ligne",
        "title": "E-commerce, Boutique Shopify / WooCommerce & DNVB",
        "short": "E-commerce",
        "naf": "47.91B",
        "sector": "Commerce & HCR",
        "flux": "B2C France/UE (e-reporting + OSS TVA) + B2B revendeurs (e-invoicing)",
        "tva": "TVA 20 % (ou 5,5 % alimentaire) + Guichet unique OSS UE au-delà de 10 000 € B2C UE",
        "edge_cases": [
            "Fort volume de transactions B2C (Stripe, PayPal, Shopify, Amazon) : e-reporting périodique des ventes B2C obligatoire au 01/09/2027 (amende 500 € par transmission manquante art. 1788 D CGI).",
            "Commandes B2B (clients pros saisissant un SIREN/TVA sur votre boutique) : doivent générer une facture électronique structurée Factur-X.",
            "Réception obligatoire depuis le 01/09/2026 pour transporteurs (Chronopost, Colissimo, DHL), logisticiens et fournisseurs français.",
        ],
        "checklist": [
            "Choisir une PA connectée à Shopify/WooCommerce/Stripe (Pennylane, Qonto ou Tiime).",
            "Collecter le SIREN des acheteurs professionnels au checkout pour routage e-invoicing.",
            "Vérifier le seuil de 10 000 € de ventes B2C intra-UE (guichet unique OSS).",
        ],
        "pas": ["pennylane", "qonto", "tiime"],
        "faq_q": "Un e-commerçant vendant uniquement aux particuliers doit-il choisir une Plateforme Agréée ?",
        "faq_a": "Oui ! D'une part pour recevoir les factures électroniques de ses fournisseurs/transporteurs français depuis le 01/09/2026, d'autre part pour transmettre son e-reporting B2C à partir du 01/09/2027.",
    },
    {
        "slug": "commercant-detail",
        "title": "Commerçant de détail & Boutique physique",
        "short": "Commerçant",
        "naf": "47.19B",
        "sector": "Commerce & HCR",
        "flux": "B2C caisse (e-reporting) + Factures clients pros (e-invoicing) + Réception fournisseurs",
        "tva": "TVA 20 % / 5,5 % / 10 % selon produits (logiciel de caisse conforme)",
        "edge_cases": [
            "Réception immédiate des factures fournisseurs/grossistes/bailleur/énergie déjà en e-invoicing depuis le 01/09/2026.",
            "Transmission des données Z de caisse B2C (e-reporting) via la PA à partir du 01/09/2027.",
            "Factures demandées au comptoir par des professionnels : nécessité de saisir leur SIREN et d'émettre en Factur-X dès 2027.",
        ],
        "checklist": [
            "Vérifier que votre logiciel de caisse est compatible avec une des 159 PA immatriculées.",
            "Activer votre PA de réception dès maintenant pour centraliser toutes les factures d'achat.",
            "Préparer une procédure rapide de facturation B2B avec SIREN client.",
        ],
        "pas": ["tiime", "pennylane", "qonto"],
        "faq_q": "Les tickets de caisse remis aux particuliers deviennent-ils des Factur-X ?",
        "faq_a": "Non, le client particulier reçoit un ticket classique (sur demande). Ce sont les totaux journaliers de caisse (e-reporting) qui seront transmis à l'administration fiscale via votre PA dès septembre 2027.",
    },
    {
        "slug": "boulanger-patissier",
        "title": "Boulanger, Pâtissier & Artisan alimentaire",
        "short": "Boulanger-pâtissier",
        "naf": "10.71C",
        "sector": "Commerce & HCR",
        "flux": "B2C comptoir (e-reporting) + B2B entreprises/restaurants/collectivités (e-invoicing)",
        "tva": "Multi-taux : 5,5 % (pain, pâtisserie à emporter), 10 % (snacking/sur place), 20 % (confiserie/alcool)",
        "edge_cases": [
            "Ventilation obligatoire sur 3 taux de TVA (5,5 %, 10 %, 20 %) dans le Z de caisse transmis en e-reporting.",
            "Livraisons de pain/viennoiseries à des restaurants, hôtels ou entreprises : ces factures B2B passent en e-invoicing structuré.",
            "Réception des factures minoteries, énergéticiens et grossistes alimentaires déjà en format électronique depuis septembre 2026.",
        ],
        "checklist": [
            "Raccorder votre boulangerie à une PA (souvent via votre cabinet comptable : Pennylane ou Tiime).",
            "Contrôler le paramétrage des 3 taux de TVA de votre caisse enregistreuse.",
            "Collecter le SIREN de vos clients professionnels (hôtels, traiteurs, entreprises).",
        ],
        "pas": ["pennylane", "tiime", "qonto"],
        "faq_q": "Une boulangerie qui livre des viennoiseries à un hôtel doit-elle émettre en Factur-X ?",
        "faq_a": "Oui, toute vente B2B entre deux assujettis français (boulangerie vers hôtel/restaurant/entreprise) passe en facturation électronique structurée au 1er septembre 2027.",
    },
    {
        "slug": "restaurateur",
        "title": "Restaurateur, Café, Brasserie & Traiteur",
        "short": "Restaurateur",
        "naf": "56.10A",
        "sector": "Commerce & HCR",
        "flux": "B2C salle/livraison (e-reporting) + Repas d'affaires/traiteur B2B (e-invoicing)",
        "tva": "TVA 10 % (consommation immédiate), 5,5 % (différé scellé), 20 % (alcools)",
        "edge_cases": [
            "Notes de restaurant pour clients professionnels : au-delà de 150 € HT (ou sur demande B2B avec SIREN), la facture doit respecter toutes les mentions EN 16931.",
            "Commissions plateformes de livraison (Uber Eats, Deliveroo) et factures fournisseurs (Metro, Transgourmet, brasseurs) : réception électronique déjà active en 2026.",
            "Prestations traiteur événementiel B2B : acomptes + soldes multi-taux (10 % nourriture / 20 % alcool et service).",
        ],
        "checklist": [
            "Activer votre PA de réception pour les grossistes HCR (Metro, Pomona, Transgourmet).",
            "Vérifier l'interfaçage de votre caisse HCR pour l'e-reporting journalier 2027.",
            "Séparer strictement les lignes TVA 10 % et 20 % sur vos devis et factures traiteur.",
        ],
        "pas": ["pennylane", "qonto", "tiime"],
        "faq_q": "Comment traiter les factures Metro ou Transgourmet en 2026 ?",
        "faq_a": "Ces grands grossistes émettent déjà en facturation électronique depuis le 1er septembre 2026. Votre PA les reçoit automatiquement et les transmet à votre comptabilité sans ressaisie manuelle.",
    },
    {
        "slug": "hotelier-gite",
        "title": "Hôtelier, Chambre d'hôtes & Gîte professionnel",
        "short": "Hôtelier & Gîte",
        "naf": "55.10Z",
        "sector": "Commerce & HCR",
        "flux": "B2C voyageurs (e-reporting) + Séminaires/déplacements pros B2B (e-invoicing)",
        "tva": "TVA 10 % (hébergement, petit-déjeuner), 20 % (alcools, salles séminaire) + Taxe de séjour hors TVA",
        "edge_cases": [
            "Taxe de séjour collectée pour la commune : exclue de la base TVA (code hors champ) mais présente sur la facture client.",
            "Commissions OTA (Booking, Expedia, Airbnb) : factures étrangères UE soumises à autoliquidation TVA et e-reporting d'acquisitions.",
            "Séminaires d'entreprises et nuits d'affaires B2B : factures structurées Factur-X avec SIREN de l'entreprise cliente.",
        ],
        "checklist": [
            "Paramétrer la ligne « Taxe de séjour » en hors champ TVA dans votre PMS / logiciel de facturation.",
            "Choisir une PA compatible avec votre PMS et votre comptable.",
            "Vérifier le traitement TVA autoliquidée des commissions Booking/Airbnb.",
        ],
        "pas": ["pennylane", "qonto", "axonaut"],
        "faq_q": "La taxe de séjour est-elle soumise à TVA dans une facture Factur-X ?",
        "faq_a": "Non. La taxe de séjour reversée à la collectivité est un élément hors champ TVA : en XML EN 16931, elle doit être isolée sans TVA afin de ne pas fausser les totaux taxables.",
    },
    {
        "slug": "coiffeur-barbier",
        "title": "Coiffeur, Barbier & Salon de coiffure",
        "short": "Coiffeur-barbier",
        "naf": "96.02A",
        "sector": "Commerce & HCR",
        "flux": "B2C salon (e-reporting 2027) + Réception fournisseurs produits/loyer (LIVE 2026)",
        "tva": "TVA 20 % (prestations et revente produits) ou Franchise 293 B (coiffeur à domicile)",
        "edge_cases": [
            "Coiffeurs à domicile en micro-entreprise : souvent en franchise de TVA 293 B mais tout de même tenus de disposer d'une PA de réception gratuite dès 2026.",
            "Salons avec caisse enregistreuse : agrégation quotidienne B2C (e-reporting) à activer avant le 01/09/2027.",
            "Fournisseurs capillaires (L'Oréal, Schwarzkopf, grossistes) : factures électroniques déjà actives.",
        ],
        "checklist": [
            "Ouvrir un compte gratuit sur une PA immatriculée (Tiime ou Indy) pour la réception fournisseurs.",
            "Vérifier la mise à jour e-reporting 2027 auprès de l'éditeur de votre logiciel de caisse salon.",
            "Suivre vos seuils micro-entreprise (77 700 € prestations / revente produits) si indépendant.",
        ],
        "pas": ["tiime", "shine", "abby"],
        "faq_q": "Un coiffeur à domicile auto-entrepreneur doit-il payer un abonnement logiciel en 2026 ?",
        "faq_a": "Non ! Plusieurs Plateformes Agréées immatriculées DGFiP (Tiime, Indy) proposent un socle gratuit suffisant pour recevoir vos factures fournisseurs et préparer l'e-reporting 2027.",
    },
    {
        "slug": "estheticienne-bien-etre",
        "title": "Esthéticienne, Institut de beauté & Praticien bien-être",
        "short": "Esthéticienne",
        "naf": "96.02B",
        "sector": "Commerce & HCR",
        "flux": "B2C soins & vente cosmétiques (e-reporting) + Réception fournisseurs (LIVE 2026)",
        "tva": "TVA 20 % ou Franchise 293 B (attention cumul prestations + revente produits)",
        "edge_cases": [
            "Activité mixte soins (prestations de services) + vente de crèmes/cosmétiques : double suivi des plafonds micro-entreprise et de la franchise de TVA.",
            "Cartes cadeaux et abonnements cures : règle d'exigibilité de la TVA à l'encaissement des acomptes ou à l'utilisation selon le type de bon.",
            "Plateformes de réservation (Planity, Treatwell) : factures d'abonnement/commission en réception électronique.",
        ],
        "checklist": [
            "Désigner votre PA de réception gratuite pour recevoir Planity, marques cosmétiques et loyers.",
            "Distinguer prestations esthétiques et ventes de produits cosmétiques dans votre livre des recettes.",
            "Préparer le suivi des seuils TVA 293 B avec notre simulateur URSSAF & TVA.",
        ],
        "pas": ["abby", "tiime", "shine"],
        "faq_q": "Les commissions Planity entrent-elles dans ma réception électronique 2026 ?",
        "faq_a": "Oui. Toutes vos factures de prestataires établis en France (plateformes de réservation, fournisseurs cosmétiques, télécoms) passent progressivement par votre Plateforme Agréée.",
    },
    {
        "slug": "garagiste-reparation-auto",
        "title": "Garagiste, Mécanicien & Carrossier automobile",
        "short": "Garagiste",
        "naf": "45.20A",
        "sector": "Commerce & HCR",
        "flux": "B2C automobilistes (e-reporting) + B2B flottes/loueurs/assurances (e-invoicing)",
        "tva": "TVA 20 % (pièces + main-d'œuvre) · Cas particulier TVA sur marge pour négoce VO",
        "edge_cases": [
            "Opérations mixtes pièces détachées + main-d'œuvre : mention obligatoire « Livraison de biens et prestations de services ».",
            "Facturation aux loueurs longue durée (ALD/Ayvens, Arval), flottes d'entreprises et compagnies d'assurances : flux B2B e-invoicing strict (rejet si numéro de dossier/immatriculation manquant).",
            "Négoce de véhicules d'occasion (TVA sur la marge art. 297 A CGI) : mention légale obligatoire « Régime particulier — Biens d'occasion » et code TVA spécifique.",
        ],
        "checklist": [
            "Activer votre PA de réception pour les distributeurs de pièces (Autodistribution, Alliance Automotive, constructeurs).",
            "Vérifier le codage des factures mixtes pièces/main-d'œuvre et véhicules d'occasion (TVA sur marge).",
            "Connecter votre DMS garage à une PA immatriculée avant septembre 2027.",
        ],
        "pas": ["axonaut", "pennylane", "qonto"],
        "faq_q": "Comment facturer un véhicule d'occasion en TVA sur la marge avec Factur-X ?",
        "faq_a": "La norme Factur-X EN 16931 prévoit la mention réglementaire « Régime particulier — Biens d'occasion » (art. 297 A CGI) sans faire apparaître de montant de TVA séparé sur la facture client.",
    },
    # --- Transport, Immobilier, Formation, Création & Autres (13) ---
    {
        "slug": "transporteur-routier",
        "title": "Transporteur routier de marchandises & Coursier",
        "short": "Transporteur",
        "naf": "49.41A",
        "sector": "Transport & Immobilier",
        "flux": "B2B chargeurs / commissionnaires (e-invoicing) + Transport intracommunautaire (e-reporting)",
        "tva": "TVA 20 % France · Autoliquidation / Exonération transport international import/export",
        "edge_cases": [
            "Délais de paiement plafonnés à 30 jours date d'émission (art. L441-11 Code de commerce) : la date horodatée par la PA devient opposable.",
            "Indexation gazole (pied de facture carburant) et péages refacturés : intégration claire dans les lignes EN 16931.",
            "Réception immédiate des factures cartes carburant (TotalEnergies, Shell), péages (Ulys/AS24) et loueurs poids lourds dès 2026.",
        ],
        "checklist": [
            "Connecter votre entreprise à une PA pour automatiser les factures carburant/péages/maintenance.",
            "Indiquer la clause légale délai 30 jours transport et les pénalités de retard (indemnité 40 €).",
            "Contrôler les factures de transport international (autoliquidation B2B UE).",
        ],
        "pas": ["qonto", "pennylane", "sellsy"],
        "faq_q": "La réforme change-t-elle le délai légal de 30 jours dans le transport routier ?",
        "faq_a": "Non, le plafond légal de 30 jours reste inchangé, mais l'horodatage officiel de dépôt sur la PA renforce la traçabilité en cas de retard de paiement.",
    },
    {
        "slug": "chauffeur-vtc-taxi",
        "title": "Chauffeur VTC, Taxi & Transport de voyageurs",
        "short": "Chauffeur VTC / Taxi",
        "naf": "49.32Z",
        "sector": "Transport & Immobilier",
        "flux": "B2C passagers (e-reporting) + Courses d'affaires B2B & Plateformes (Uber/Bolt)",
        "tva": "TVA 10 % (transport de personnes) · TVA 20 % (mise à disposition avec chauffeur / commissions)",
        "edge_cases": [
            "Commissions plateformes UE (Uber BV Pays-Bas, Bolt Estonie) : autoliquidation de TVA obligatoire à 20 % (même en franchise 293 B, numéro TVA intracommunautaire obligatoire !) et e-reporting d'acquisitions.",
            "Facturation directe à des hôtels, conciergeries ou entreprises : e-invoicing B2B avec taux 10 % (transfert point à point) vs 20 % (mise à disposition).",
            "Auto-facturation émise par les plateformes au nom du chauffeur : nécessite un mandat de facturation explicite.",
        ],
        "checklist": [
            "Demander votre numéro de TVA intracommunautaire au SIE si vous travaillez avec Uber ou Bolt.",
            "Ouvrir une PA gratuite (Indy, Tiime ou Shine) pour la réception de vos charges (leasing, entretien, assurance).",
            "Vérifier le taux exact (10 % transfert vs 20 % mise à disposition) sur vos courses privées B2B.",
        ],
        "pas": ["indy", "shine", "tiime"],
        "faq_q": "Un chauffeur VTC en franchise de TVA qui roule sur Uber doit-il déclarer la TVA sur les commissions ?",
        "faq_a": "Oui ! Les commissions facturées par Uber BV (Pays-Bas) sont soumises à l'autoliquidation de TVA en France, même si vous bénéficiez de la franchise en base sur vos propres courses.",
    },
    {
        "slug": "agent-immobilier",
        "title": "Agent immobilier & Mandataire immobilier (IAD, Safti…)",
        "short": "Agent & Mandataire immo",
        "naf": "68.31Z",
        "sector": "Transport & Immobilier",
        "flux": "Mandataires : 100 % B2B vers réseau (e-invoicing) · Agences : B2C honoraires + B2B",
        "tva": "TVA 20 % sur honoraires d'entremise (exigible à la signature de l'acte authentique / encaissement)",
        "edge_cases": [
            "Mandataires indépendants (agent commercial RSAC) : vous facturez vos rétrocessions de commissions directement à votre réseau (B2B France) -> 100 % dans le champ de l'e-invoicing !",
            "Agences immobilières : honoraires de vente facturés aux particuliers (e-reporting B2C) et factures de commercialisation promoteurs / baux pro (e-invoicing B2B).",
            "Réception immédiate des factures portails d'annonces (SeLoger, Leboncoin, Bien'ici) dès septembre 2026.",
        ],
        "checklist": [
            "Pour les mandataires : activer votre PA (Indy ou Tiime) pour recevoir les factures réseau/packs et préparer l'émission 2027.",
            "Mentionner votre numéro RSAC (mandataire) ou carte professionnelle CPI (agence) sur vos Factur-X.",
            "Surveiller le franchissement rapide du seuil de franchise TVA dès 2 à 3 ventes dans l'année.",
        ],
        "pas": ["indy", "tiime", "qonto"],
        "faq_q": "Un mandataire immobilier facturant son réseau en auto-facturation est-il concerné ?",
        "faq_a": "Oui. Même si le réseau génère des factures par mandat (auto-facturation), le flux B2B transitera par les Plateformes Agréées et vous devez disposer d'une PA de réception dès 2026.",
    },
    {
        "slug": "diagnostiqueur-immobilier",
        "title": "Diagnostiqueur immobilier (DPE, Amiante, Électricité)",
        "short": "Diagnostiqueur immo",
        "naf": "71.20B",
        "sector": "Transport & Immobilier",
        "flux": "B2C vendeurs/bailleurs (e-reporting) + B2B agences, notaires, bailleurs (e-invoicing)",
        "tva": "TVA 20 % (prestations techniques de contrôle)",
        "edge_cases": [
            "Forte proportion de factures adressées à des professionnels (notaires, agences immobilières, marchands de biens, bailleurs sociaux) : flux e-invoicing B2B avec référence dossier/parcelle.",
            "Adresse du bien diagnostiqué systématiquement différente de l'adresse de facturation (notaire/propriétaire) -> champ adresse de livraison obligatoire.",
            "Réception électronique des frais de certification, calibration d'appareils (plomb/amiante) et logiciels DPE.",
        ],
        "checklist": [
            "Renseigner l'adresse exacte du bien contrôlé et le SIREN du donneur d'ordre pro sur chaque facture.",
            "Activer votre PA de réception dès maintenant.",
            "Connecter votre logiciel métier à une PA immatriculée pour automatiser les envois notaires/agences.",
        ],
        "pas": ["tiime", "axonaut", "indy"],
        "faq_q": "Dois-je mettre le SIREN du notaire ou du propriétaire vendeur sur ma facture ?",
        "faq_a": "Le SIREN à indiquer est celui du véritable client facturé (redevable de la prestation) : le vendeur s'il est une société/SCI assujettie, ou le notaire/agence uniquement s'ils vous mandatent en leur nom propre.",
    },
    {
        "slug": "syndic-gestion-locative",
        "title": "Syndic de copropriété & Administrateur de biens",
        "short": "Syndic & Gestion locative",
        "naf": "68.32A",
        "sector": "Transport & Immobilier",
        "flux": "Réception fournisseurs copropriétés + Honoraires B2B/B2C",
        "tva": "TVA 20 % sur honoraires de gestion/syndic · Loyers nus exonérés",
        "edge_cases": [
            "Distinction majeure : les syndicats de copropriétaires non assujettis à la TVA ne sont pas dans le champ e-invoicing, MAIS le cabinet de syndic (société commerciale) est 100 % soumis à la réception 2026 et à l'émission/e-reporting 2027.",
            "Gestion des baux commerciaux assujettis à TVA : les avis d'échéance / factures de loyers commerciaux soumis à TVA entrent dans l'e-invoicing B2B.",
            "Contrôle massif de factures artisans BTP : un inspecteur Factur-X accélère la validation avant imputation.",
        ],
        "checklist": [
            "Séparer les flux propres du cabinet (PA obligatoire) et les comptes mandants des syndicats non assujettis.",
            "Identifier les baux commerciaux avec option TVA soumis à la facturation électronique.",
            "Vérifier l'interopérabilité de votre logiciel de gestion immobilière avec une PA DGFiP.",
        ],
        "pas": ["pennylane", "sellsy", "qonto"],
        "faq_q": "Les loyers commerciaux soumis à TVA devront-ils être émis en Factur-X ?",
        "faq_a": "Oui ! Lorsqu'un bail commercial est assujetti à la TVA (de plein droit ou sur option), les factures de loyers entre assujettis français relèvent de la facturation électronique obligatoire.",
    },
    {
        "slug": "formateur-qualiopi",
        "title": "Formateur indépendant & Organisme de formation (Qualiopi)",
        "short": "Formateur Qualiopi",
        "naf": "85.59A",
        "sector": "Formation & Création",
        "flux": "B2B entreprises & OPCO (e-invoicing) + B2G CPF/France Travail (Chorus Pro)",
        "tva": "Exonération TVA formation professionnelle (art. 261-4-4°-a CGI avec attestation DREETS) ou TVA 20 %",
        "edge_cases": [
            "Attention piège fréquent : les organismes de formation exonérés au titre de l'art. 261-4-4°-a (attestation fiscale DREETS) restent hors e-invoicing sur ces seules prestations exonérées, MAIS toute mission de conseil, coaching ou formation non exonérée impose PA + Factur-X !",
            "Facturation aux OPCO, écoles ou entreprises en sous-traitance : bien distinguer l'exonération formation (art. 261-4-4°) et la franchise micro-entreprise (art. 293 B).",
            "Financements publics (France Travail, collectivités, universités) : dépôt obligatoire sur Chorus Pro.",
        ],
        "checklist": [
            "Inscrire votre NDA (numéro de déclaration d'activité) et la référence légale d'exonération exacte sur chaque facture.",
            "Activer une PA de réception gratuite pour toutes vos dépenses pro (salles, outils, sous-traitants).",
            "Vérifier si vos prestations de conseil/audit annexes vous rendent assujetti à l'e-invoicing 2027.",
        ],
        "pas": ["indy", "tiime", "abby"],
        "faq_q": "Un formateur exonéré de TVA (art. 261-4-4° CGI) doit-il émettre en Factur-X aux OPCO ?",
        "faq_a": "Les prestations de formation professionnelle continue strictement exonérées au titre de l'art. 261-4-4°-a du CGI bénéficient d'une exclusion d'e-invoicing, mais beaucoup d'OPCO et d'écoles demandent déjà le PDF/A-3 structuré — et la réception fournisseur via PA reste recommandée/obligatoire dès la moindre activité annexe taxable.",
    },
    {
        "slug": "coach-professionnel",
        "title": "Coach professionnel, Mentor & Consultant RH",
        "short": "Coach professionnel",
        "naf": "85.59B",
        "sector": "Formation & Création",
        "flux": "B2B entreprises (e-invoicing) + B2C particuliers (e-reporting)",
        "tva": "TVA 20 % ou Franchise art. 293 B (le coaching n'est généralement pas exonéré 261-4-4°)",
        "edge_cases": [
            "Sauf action de formation certifiée Qualiopi avec attestation fiscale, le coaching est taxable à 20 % (ou en franchise 293 B) -> 100 % soumis à la réforme 2026–2027.",
            "Accompagnements de particuliers vendus via Stripe/Systeme.io : soumis à l'e-reporting B2C au 01/09/2027.",
            "Facturation de bilans de compétences ou coaching dirigeants aux entreprises : SIREN client + Factur-X EN 16931.",
        ],
        "checklist": [
            "Ouvrir une PA gratuite (Indy, Tiime ou Abby) pour recevoir vos factures d'outils et salles.",
            "Mettre en conformité vos factures B2B avec les 4 mentions obligatoires 2026–2027.",
            "Suivre vos encaissements Stripe/virements pour préparer l'e-reporting B2C.",
        ],
        "pas": ["indy", "abby", "tiime"],
        "faq_q": "Les ventes de programmes en ligne aux particuliers passent-elles en Factur-X ?",
        "faq_a": "Non pour l'envoi de Factur-X au particulier, mais vos ventes B2C (Stripe, cartes, virements) devront être déclarées périodiquement en e-reporting via votre PA à partir du 1er septembre 2027.",
    },
    {
        "slug": "photographe-videaste",
        "title": "Photographe, Vidéaste & Artiste-auteur",
        "short": "Photographe & Vidéaste",
        "naf": "74.20Z",
        "sector": "Formation & Création",
        "flux": "B2B marques/agences/presse (e-invoicing) + B2C mariages/portraits (e-reporting)",
        "tva": "TVA 10 % (cessions de droits d'auteur) · TVA 20 % (prestations techniques / mariages) · Franchise 293 B",
        "edge_cases": [
            "Taux de TVA différenciés : 10 % sur les cessions de droits d'auteur (art. 279 g CGI) vs 20 % sur les prestations de prise de vue technique ou tirages non originaux.",
            "Double statut fréquent (Artiste-auteur URSSAF Limousin + micro-entreprise BIC/BNC) : un même SIREN avec deux natures de facturation à bien ventiler.",
            "Cessions de droits précises (durée, territoire, supports) à conserver dans le texte du PDF/A-3.",
        ],
        "checklist": [
            "Activer votre PA de réception gratuite (achats boîtiers, optiques, studios, Adobe/cloud).",
            "Vérifier le taux de TVA applicable (franchise 293 B, 10 % droits d'auteur, 20 % technique).",
            "Intégrer les 4 mentions légales 2026–2027 sur vos notes d'auteur et factures agences.",
        ],
        "pas": ["indy", "abby", "tiime"],
        "faq_q": "Les artistes-auteurs bénéficiant de la franchise de TVA spécifique sont-ils concernés ?",
        "faq_a": "Oui dès lors qu'ils sont assujettis établis en France (même en franchise art. 293 B) : réception électronique via PA depuis septembre 2026 et émission B2B / e-reporting B2C au 1er septembre 2027.",
    },
    {
        "slug": "graphiste-designer",
        "title": "Graphiste, UI/UX Designer & Directeur artistique",
        "short": "Graphiste & Designer",
        "naf": "74.10Z",
        "sector": "Formation & Création",
        "flux": "B2B agences/startups/PME (e-invoicing) + Clients étrangers (e-reporting international)",
        "tva": "Franchise 293 B · TVA 10 % (cession droits d'auteur) ou 20 % (design produit/UI/UX)",
        "edge_cases": [
            "Factures d'acompte (30–50 % au brief) et soldes à la livraison des fichiers sources : gestion rigoureuse des codes facture 386 et BT-113 en Factur-X.",
            "Clients hors France (agences UK, US, Suisse, Belgique) : mention autoliquidation UE ou hors champ TVA + e-reporting international.",
            "Distinction claire entre prestation de conception graphique et cession de droits d'exploitation.",
        ],
        "checklist": [
            "Choisir une PA gratuite simple (Tiime, Indy ou Abby) pour recevoir vos factures d'impression et logiciels.",
            "Auditer gratuitement vos modèles PDF actuels sur notre inspecteur Factur-X 2027.",
            "Contrôler votre seuil de franchise TVA et vos cotisations URSSAF 2026.",
        ],
        "pas": ["abby", "indy", "tiime"],
        "faq_q": "Un graphiste freelance en micro-entreprise peut-il garder un outil gratuit en 2026–2027 ?",
        "faq_a": "Oui. Des PA immatriculées comme Tiime ou Indy offrent la facturation électronique gratuite, et FacturKit 2027 vous permet de générer et vérifier vos Factur-X en local sans abonnement mensuel.",
    },
    {
        "slug": "redacteur-traducteur",
        "title": "Rédacteur web, Copywriter & Traducteur indépendant",
        "short": "Rédacteur & Traducteur",
        "naf": "74.30Z",
        "sector": "Formation & Création",
        "flux": "B2B agences/éditeurs France (e-invoicing) + Export agences UE/US (e-reporting international)",
        "tva": "Franchise art. 293 B ou TVA 20 % / Autoliquidation B2B intracommunautaire (DES obligatoire)",
        "edge_cases": [
            "Clientèle très souvent européenne (agences de traduction en Allemagne, Belgique, Irlande, Pays-Bas) : exige un numéro de TVA intracommunautaire, une Déclaration Européenne de Services (DES) mensuelle et l'e-reporting international en 2027.",
            "Micro-factures récurrentes au mot ou au feuillet : automatisation recommandée pour éviter la saisie manuelle.",
            "Réception fournisseurs français via PA obligatoire depuis le 01/09/2026.",
        ],
        "checklist": [
            "Vérifier votre numéro de TVA intracommunautaire pour vos agences clientes dans l'UE.",
            "Activer votre PA gratuite (Indy ou Tiime) pour la réception des factures.",
            "Ajouter le SIREN client et la catégorie « Prestation de services » sur toutes vos factures FR.",
        ],
        "pas": ["indy", "abby", "tiime"],
        "faq_q": "Un traducteur en franchise de TVA qui facture une agence allemande doit-il demander un numéro de TVA ?",
        "faq_a": "Oui ! Pour facturer des prestations B2B à une entreprise située dans un autre pays de l'UE, un numéro de TVA intracommunautaire (et le dépôt de la DES sur douane.gouv.fr) est obligatoire même en franchise 293 B.",
    },
    {
        "slug": "agence-communication-marketing",
        "title": "Agence de communication, SEO & Marketing digital",
        "short": "Agence com & SEO",
        "naf": "73.11Z",
        "sector": "Formation & Création",
        "flux": "B2B PME/ETI/Marques (e-invoicing) + Achats médias étrangers (Meta/Google Ads)",
        "tva": "TVA 20 % · Autoliquidation sur achats régies UE (Google Ireland, Meta Ireland)",
        "edge_cases": [
            "Refacturation d'espaces publicitaires (loi Sapin : mandat transparent obligatoire si achat média au nom de l'annonceur).",
            "Factures Google Ads / Meta Ads / LinkedIn (Irlande) : autoliquidation TVA intracommunautaire et e-reporting d'acquisitions.",
            "Abonnements mensuels SEO/Social Media (retainers) : automatisation idéale via PA connectée CRM.",
        ],
        "checklist": [
            "Connecter votre outil CRM/facturation à une PA DGFiP (Axonaut, Sellsy ou Pennylane).",
            "Séparer honoraires d'agence et budgets médias dans vos factures structurées.",
            "Automatiser le suivi des encaissements et relances clients.",
        ],
        "pas": ["axonaut", "sellsy", "pennylane"],
        "faq_q": "Comment traiter les factures Google Ads ou Meta Ads dans la réforme 2026–2027 ?",
        "faq_a": "Les régies établies en Irlande n'émettent pas via le réseau domestique français, mais vos achats de services intra-UE restent soumis à autoliquidation TVA et à l'e-reporting d'acquisitions.",
    },
    {
        "slug": "societe-nettoyage-proprete",
        "title": "Société de nettoyage, Propreté & Services aux locaux",
        "short": "Société de nettoyage",
        "naf": "81.21Z",
        "sector": "Services B2B",
        "flux": "B2B bureaux/copropriétés/commerces (e-invoicing) + B2G (Chorus Pro)",
        "tva": "TVA 20 % (nettoyage locaux pros) · Attention sous-traitance et contrats récurrents",
        "edge_cases": [
            "Facturation mensuelle récurrente sur des dizaines de sites clients : l'adresse de chaque site nettoyé (adresse d'exécution) doit figurer sur la facture structurée.",
            "Missions ponctuelles de remise en état fin de chantier en sous-traitance BTP : vigilance sur les règles d'autoliquidation BTP selon la nature exacte des travaux.",
            "Contrôle de la trésorerie et des statuts de règlement (TVA sur les encaissements).",
        ],
        "checklist": [
            "Paramétrer la facturation récurrente Factur-X avec SIREN et adresse d'intervention par site.",
            "Activer votre PA de réception pour vos fournisseurs produits d'entretien et véhicules.",
            "Vérifier vos numéros d'engagement Chorus Pro pour les marchés mairies/écoles.",
        ],
        "pas": ["axonaut", "pennylane", "qonto"],
        "faq_q": "Dois-je mentionner l'adresse de chaque bureau nettoyé sur ma facture mensuelle ?",
        "faq_a": "Oui, dès lors que le lieu d'exécution diffère du siège social du client, la mention de l'adresse de livraison/exécution fait partie des 4 mentions obligatoires 2026–2027.",
    },
    {
        "slug": "courtier-assurance-credit",
        "title": "Courtier en assurance, Crédit & CGP (ORIAS)",
        "short": "Courtier & CGP",
        "naf": "66.22Z",
        "sector": "Conseil & Finance",
        "flux": "Commissions courtage exonérées + Honoraires conseil taxables · Réception fournisseurs",
        "tva": "Exonération TVA courtage assurance/crédit (art. 261 C CGI) · TVA 20 % sur conseil pur",
        "edge_cases": [
            "Les commissions d'intermédiation en assurance et crédit bancaire (art. 261 C CGI) sont exonérées de TVA et hors champ e-invoicing, MAIS les honoraires de conseil patrimonial/audit non liés à une intermédiation sont soumis à TVA 20 % -> PA obligatoire.",
            "Réception électronique des factures fournisseurs du cabinet (CRM, logiciels, ORIAS, locaux) dès 2026.",
            "Double suivi comptable indispensable en cas d'assujettissement partiel (prorata de déduction TVA / taxe sur les salaires).",
        ],
        "checklist": [
            "Identifier précisément la part exonérée (art. 261 C) et la part d'honoraires de conseil soumise à TVA.",
            "Ouvrir une PA immatriculée pour la réception des factures fournisseurs et vos honoraires B2B.",
            "Conserver votre numéro d'immatriculation ORIAS sur l'ensemble de vos factures PDF/A-3.",
        ],
        "pas": ["pennylane", "indy", "qonto"],
        "faq_q": "Un courtier en assurance 100 % exonéré de TVA est-il soumis à la facturation électronique ?",
        "faq_a": "Les opérations exonérées visées à l'article 261 C du CGI sont hors champ d'émission e-invoicing, mais dès que vous facturez du conseil non exonéré ou recevez des factures fournisseurs en société, disposer d'une PA devient essentiel.",
    },
    {
        "slug": "association-loi-1901",
        "title": "Association loi 1901 (à activités lucratives ou mixtes)",
        "short": "Association loi 1901",
        "naf": "94.99Z",
        "sector": "Services B2B",
        "flux": "Assujettie si activités lucratives > franchise · Hors champ si 100 % non lucrative",
        "tva": "Hors TVA si gestion désintéressée non lucrative · Assujettie si activités commerciales > seuil annuel",
        "edge_cases": [
            "Critère décisif : une association 100 % non lucrative (non assujettie à la TVA) n'est pas soumise à la réforme ; en revanche, une association fiscalisée (secteur lucratif, sponsoring B2B, billetterie commerciale au-delà de la franchise) est soumise à la réception 2026 et à l'émission/e-reporting 2027.",
            "Subventions publiques pures : hors champ TVA et hors e-invoicing (à distinguer des prestations de services commandées par une collectivité sur Chorus Pro).",
            "Reçus fiscaux de dons : totalement distincts des factures électroniques.",
        ],
        "checklist": [
            "Vérifier avec votre comptable si l'association dispose d'un secteur lucratif assujetti à la TVA.",
            "Si assujettie (même partiellement), activer une PA gratuite (Tiime ou Qonto Associations).",
            "Distinguer clairement subventions, dons, cotisations et prestations facturées en B2B.",
        ],
        "pas": ["qonto", "tiime", "pennylane"],
        "faq_q": "Une petite association sportive non assujettie à la TVA doit-elle prendre une PA ?",
        "faq_a": "Non. Seules les structures assujetties à la TVA en France entrent dans le champ de la réforme. Une association strictement non lucrative et non assujettie n'est pas obligée de choisir une PA.",
    },
    {
        "slug": "agriculteur-viticulteur",
        "title": "Exploitant agricole, Viticulteur & Producteur fermier",
        "short": "Agriculteur & Viticulteur",
        "naf": "01.11Z",
        "sector": "Agriculture & Production",
        "flux": "B2B coopératives/négociants/restaurants (e-invoicing) + Vente directe ferme/marchés (e-reporting)",
        "tva": "TVA agricole 5,5 % / 10 % / 20 % (alcools/vin) · Remboursement forfaitaire agricole (RFA) hors TVA",
        "edge_cases": [
            "Exploitants au régime simplifié agricole (RSA) : pleinement assujettis -> réception obligatoire depuis le 01/09/2026 (coopératives, fournisseurs intrants, matériel) et émission B2B / e-reporting vente directe au 01/09/2027.",
            "Auto-facturation très fréquente par les coopératives agricoles et négociants en vins : les flux transiteront par les PA (mandat d'auto-facturation à jour).",
            "Vente de vin/spiritueux : droits d'accises et TVA 20 % vs produits alimentaires fermiers à 5,5 %.",
        ],
        "checklist": [
            "Vérifier votre régime TVA (RSA assujetti = PA obligatoire ; RFA non assujetti = hors champ).",
            "Connecter votre exploitation à une PA compatible avec votre centre de gestion (CERFRANCE / Pennylane / Tiime).",
            "Mettre à jour vos mandats d'auto-facturation avec vos coopératives et négociants.",
        ],
        "pas": ["tiime", "pennylane", "qonto"],
        "faq_q": "Les bordereaux d'auto-facturation de ma coopérative agricole passent-ils en Factur-X ?",
        "faq_a": "Oui pour les exploitants assujettis (RSA). La coopérative émettra la facture électronique en votre nom via sa Plateforme Agréée, et votre PA en assurera la réception et l'archivage.",
    },
]

assert len(PROFESSIONS) == 50, f"Expected 50 professions, got {len(PROFESSIONS)}"
assert len({p["slug"] for p in PROFESSIONS}) == 50, "Duplicate slugs detected!"

SHARED_STYLE = """
    :root { --border: var(--border-light, #E2E0D8); --muted: var(--ink-muted, #64748B); --accent: var(--accent-blue, #1D4ED8); --text: var(--ink-primary, #0F172A); }
    .metier-hero { padding: 48px 0 36px; border-bottom: 1px solid var(--border); background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%); }
    .breadcrumb { font-size: 0.85rem; color: var(--muted); margin-bottom: 14px; }
    .breadcrumb a { color: var(--accent); text-decoration: none; font-weight: 600; }
    .naf-pill { display: inline-flex; align-items: center; gap: 8px; padding: 5px 12px; border-radius: 999px; font-size: 0.82rem; font-weight: 700; background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; margin-bottom: 12px; }
    .metier-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 18px; margin-top: 22px; }
    .info-box { background: #fff; border: 1px solid var(--border); border-radius: 12px; padding: 20px; box-shadow: 0 2px 8px rgba(15,23,42,0.03); }
    .info-box h3 { margin-top: 0; font-size: 1.05rem; margin-bottom: 10px; }
    .pa-card-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 18px; margin-top: 18px; }
    .pa-rec-card { background: #fff; border: 1px solid var(--border); border-radius: 12px; padding: 20px; display: flex; flex-direction: column; justify-content: space-between; }
    .pa-rec-badge { display: inline-block; font-size: 0.76rem; font-weight: 700; color: #047857; background: #ecfdf5; border: 1px solid #a7f3d0; padding: 3px 9px; border-radius: 999px; margin-bottom: 8px; }
    .cta-strip { background: #0f172a; color: #f8fafc; border-radius: 14px; padding: 26px; margin-top: 32px; display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 18px; }
    .cta-strip h3 { color: #fff; margin: 0 0 6px; }
    .cta-strip p { color: #cbd5e1; margin: 0; max-width: 620px; }
    .cta-actions { display: flex; flex-wrap: wrap; gap: 10px; }
    .btn-light { background: #fff; color: #0f172a; padding: 11px 16px; border-radius: 8px; font-weight: 700; text-decoration: none; font-size: 0.92rem; }
    .btn-accent-solid { background: #2563eb; color: #fff; padding: 11px 16px; border-radius: 8px; font-weight: 700; text-decoration: none; font-size: 0.92rem; }
    .check-list { padding-left: 20px; margin: 10px 0 0; }
    .check-list li { margin-bottom: 9px; line-height: 1.55; }
    .sibling-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 12px; margin-top: 14px; }
    .sibling-link { display: block; padding: 12px 14px; border: 1px solid var(--border); border-radius: 10px; background: #fff; text-decoration: none; color: var(--text); font-weight: 600; font-size: 0.9rem; }
    .sibling-link span { display: block; font-size: 0.78rem; color: var(--muted); font-weight: 500; margin-top: 2px; }
    .sibling-link:hover { border-color: #2563eb; }
    .dir-controls { display: flex; flex-wrap: wrap; gap: 10px; margin: 20px 0; align-items: center; }
    .dir-search { flex: 1 1 260px; padding: 11px 14px; border: 1px solid var(--border); border-radius: 8px; font-size: 0.95rem; }
    .dir-pill { padding: 7px 13px; border-radius: 999px; border: 1px solid var(--border); background: #fff; font-weight: 600; font-size: 0.84rem; cursor: pointer; }
    .dir-pill[aria-pressed="true"] { background: #0f172a; color: #fff; border-color: #0f172a; }
    .metier-card { display: block; background: #fff; border: 1px solid var(--border); border-radius: 12px; padding: 18px; text-decoration: none; color: inherit; transition: border-color 0.15s ease; }
    .metier-card:hover { border-color: #2563eb; }
    .disclosure-note { font-size: 0.8rem; color: var(--muted); margin-top: 12px; }
"""


def render_header(prefix: str) -> str:
    return f"""  <header class="site-header">
    <div class="container header-inner">
      <a class="brand-lockup" href="{prefix}index.html" aria-label="YGN — FacturKit Accueil">
        <span class="brand-mark" aria-hidden="true">FK</span>
        <span class="brand-text">
          <span class="brand-name">YGN — FacturKit</span>
          <span class="brand-sub">Factur-X 2026–2027 &amp; Pilotage TPE</span>
        </span>
      </a>
      <nav class="header-nav" aria-label="Navigation principale">
        <a class="nav-link" href="{prefix}audit-facture-gratuit.html?mode=fx">Inspecteur Factur-X</a>
        <a class="nav-link" href="{prefix}comparateur-pa-2026.html">Comparateur PA</a>
        <a class="nav-link" href="{prefix}simulateur-statut-urssaf-2026.html">Simulateur URSSAF</a>
        <a class="nav-link" href="{prefix}metiers/index.html">50 Métiers (NAF)</a>
        <a class="btn-header" href="{prefix}index.html#distributeur-b2b">Kits dès 19 €</a>
      </nav>
    </div>
  </header>"""


def render_footer(prefix: str) -> str:
    return f"""  <footer class="site-footer">
    <div class="container">
      <p>
        <strong>YGN — FacturKit 2027</strong> · Outillage local Factur-X 1.09.2 / EN 16931 sans abonnement ·
        <a href="{prefix}index.html">Accueil</a> ·
        <a href="{prefix}comparateur-pa-2026.html">Comparateur 159 PA</a> ·
        <a href="{prefix}simulateur-statut-urssaf-2026.html">Simulateur URSSAF 2026</a> ·
        <a href="{prefix}metiers/index.html">Annuaire 50 Métiers</a> ·
        <a href="{prefix}audit-facture-gratuit.html?mode=fx">Inspecteur Gratuit</a> ·
        <a href="{prefix}en.html">English</a>
      </p>
      <p class="disclosure-note">Information réglementaire indépendante (LFI 2026 art. 123, Factur-X 1.09.2 / ZUGFeRD 2.5.2, annuaire DGFiP 159 PA). Certains liens vers des Plateformes Agréées peuvent inclure un suivi partenaire sans surcoût pour vous.</p>
    </div>
  </footer>"""


def build_profession_page(prof: dict, siblings: list[dict]) -> str:
    slug = prof["slug"]
    url = f"{SITE_BASE}/metiers/{slug}.html"
    title_h = html.escape(prof["title"])
    short_h = html.escape(prof["short"])
    naf_h = html.escape(prof["naf"])
    sector_h = html.escape(prof["sector"])
    meta_desc = (
        f"Facturation électronique 2026–2027 pour {prof['title']} (NAF {prof['naf']}) : "
        f"réception obligatoire 01/09/2026, émission Factur-X 1.09.2 au 01/09/2027, cas TVA/e-reporting et meilleures Plateformes Agréées."
    )

    faq_items = [
        {
            "@type": "Question",
            "name": f"Quelles sont les dates obligatoires Factur-X pour un(e) {prof['short']} (NAF {prof['naf']}) ?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "La réception électronique via une Plateforme Agréée (PA) immatriculée est obligatoire depuis le 1er septembre 2026 pour toutes les entreprises assujetties établies en France, y compris en franchise de TVA (art. 293 B). L'émission structurée Factur-X 1.09.2 et l'e-reporting s'appliquent aux TPE/PME et indépendants au 1er septembre 2027 (amendes LFI 2026 art. 123 : 50 €/facture, 500 € par e-reporting manquant, 500 € puis 1 000 €/trimestre sans PA).",
            },
        },
        {
            "@type": "Question",
            "name": prof["faq_q"],
            "acceptedAnswer": {"@type": "Answer", "text": prof["faq_a"]},
        },
        {
            "@type": "Question",
            "name": f"Quelle Plateforme Agréée (PA) choisir en {prof['naf']} ?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "Les solutions les plus adaptées au profil "
                + prof["short"]
                + " sont "
                + ", ".join(PA_INFO[k][0] for k in prof["pas"])
                + ", complétées si besoin par un outillage local hors-ligne (FacturKit 2027) pour auditer vos fichiers PDF/A-3 sans abonnement.",
            },
        },
    ]

    json_ld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "FacturKit 2027", "item": f"{SITE_BASE}/"},
                    {"@type": "ListItem", "position": 2, "name": "Métiers & Codes NAF", "item": f"{SITE_BASE}/metiers/"},
                    {"@type": "ListItem", "position": 3, "name": f"{prof['short']} ({prof['naf']})", "item": url},
                ],
            },
            {"@type": "FAQPage", "mainEntity": faq_items},
        ],
    }

    edge_html = "\n".join(f"            <li>{html.escape(item)}</li>" for item in prof["edge_cases"])
    check_html = "\n".join(f"            <li>{html.escape(item)}</li>" for item in prof["checklist"])

    pa_cards = []
    for key in prof["pas"]:
        name, slot, href, badge, price = PA_INFO[key]
        pa_cards.append(
            f"""          <article class="pa-rec-card">
            <div>
              <span class="pa-rec-badge">{html.escape(badge)}</span>
              <h3 style="margin:4px 0 6px;">{html.escape(name)}</h3>
              <p style="font-size:0.88rem;color:var(--muted);margin:0 0 12px;">{html.escape(price)}</p>
            </div>
            <a class="btn-outline" style="text-align:center;" href="{href}" data-affiliate-slot="{slot}" target="_blank" rel="noopener noreferrer">Découvrir {html.escape(name)} →</a>
          </article>"""
        )
    pa_cards_html = "\n".join(pa_cards)

    sib_html = "\n".join(
        f"""          <a class="sibling-link" href="./{s['slug']}.html">{html.escape(s['short'])}<span>NAF {html.escape(s['naf'])} · {html.escape(s['sector'])}</span></a>"""
        for s in siblings
    )

    faq_html = "\n".join(
        f"""        <details class="info-box" style="margin-bottom:12px;">
          <summary style="font-weight:700;cursor:pointer;">{html.escape(q['name'])}</summary>
          <p style="margin:10px 0 0;color:var(--muted);line-height:1.6;">{html.escape(q['acceptedAnswer']['text'])}</p>
        </details>"""
        for q in faq_items
    )

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Facture Électronique &amp; Factur-X 2026–2027 : {title_h} (NAF {naf_h}) | FacturKit</title>
  <meta name="description" content="{html.escape(meta_desc)}">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{url}">
  <link rel="icon" type="image/svg+xml" href="../favicon.svg">
  <meta property="og:type" content="article">
  <meta property="og:locale" content="fr_FR">
  <meta property="og:title" content="Factur-X 2026–2027 pour {title_h} (NAF {naf_h})">
  <meta property="og:description" content="{html.escape(meta_desc)}">
  <meta property="og:url" content="{url}">
  <script type="application/ld+json">
{json.dumps(json_ld, ensure_ascii=False, indent=2)}
  </script>
  <link rel="stylesheet" href="../styles.css">
  <style>{SHARED_STYLE}</style>
</head>
<body>
{render_header("../")}

  <main>
    <section class="metier-hero">
      <div class="container">
        <div class="breadcrumb">
          <a href="../index.html">FacturKit 2027</a> › <a href="./index.html">50 Métiers &amp; Codes NAF</a> › {short_h}
        </div>
        <div class="naf-pill">Code NAF {naf_h} · {sector_h} · Réforme en vigueur nov. 2026</div>
        <h1>Facturation électronique &amp; Factur-X 2026–2027 : {title_h}</h1>
        <p class="hero-lead">
          Guide opérationnel dédié aux professionnels <strong>{title_h} (NAF {naf_h})</strong> : obligations actives depuis le <strong>1er septembre 2026</strong> (réception obligatoire via l'une des <strong>159 Plateformes Agréées DGFiP</strong>), bascule d'émission <strong>Factur-X 1.09.2 / ZUGFeRD 2.5.2</strong> au <strong>1er septembre 2027</strong>, cas particuliers TVA et choix d'outillage sans surcoût.
        </p>
        <div class="hero-cta-row">
          <a href="../audit-facture-gratuit.html?mode=fx" class="btn-primary">Vérifier une facture Factur-X (Gratuit)</a>
          <a href="../comparateur-pa-2026.html" class="btn-outline">Comparer les Plateformes Agréées</a>
          <a href="../simulateur-statut-urssaf-2026.html" class="btn-outline">Simuler URSSAF &amp; Statut 2026</a>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="metier-grid">
          <article class="info-box">
            <h3>1. Calendrier légal &amp; Sanctions (LFI 2026 art. 123)</h3>
            <p style="margin:0 0 8px;"><strong>Depuis le 01/09/2026 (EN VIGUEUR) :</strong> réception obligatoire de factures électroniques via une PA immatriculée (amende <strong>500 €</strong> puis <strong>1 000 €/trim.</strong> sans PA après mise en demeure).</p>
            <p style="margin:0;"><strong>Au 01/09/2027 (TPE/PME &amp; Micro) :</strong> émission structurée Factur-X 1.09.2 / EN 16931 et e-reporting (amendes <strong>50 €/facture</strong> art. 1737 III et <strong>500 €/e-reporting</strong> art. 1788 D).</p>
          </article>
          <article class="info-box">
            <h3>2. Profil de flux &amp; Régime TVA ({naf_h})</h3>
            <p style="margin:0 0 8px;"><strong>Flux dominants :</strong> {html.escape(prof['flux'])}</p>
            <p style="margin:0;"><strong>Régime TVA usuel :</strong> {html.escape(prof['tva'])}</p>
          </article>
        </div>

        <div class="metier-grid" style="margin-top:20px;">
          <article class="info-box">
            <h3>Cas particuliers de facturation à maîtriser ({short_h})</h3>
            <ul class="check-list">
{edge_html}
            </ul>
          </article>
          <article class="info-box">
            <h3>Checklist de mise en conformité 2026–2027</h3>
            <ul class="check-list">
{check_html}
            </ul>
          </article>
        </div>

        <div style="margin-top:34px;">
          <h2>Plateformes Agréées (PA) &amp; Outils recommandés pour {short_h}</h2>
          <p style="color:var(--muted);margin-top:4px;">Sélection adaptée au code NAF {naf_h}. Consultez la grille complète sur notre <a href="../comparateur-pa-2026.html">Comparateur des Plateformes Agréées 2026–2027</a>.</p>
          <div class="pa-card-grid">
{pa_cards_html}
          </div>
          <p class="disclosure-note">Transparence : liens officiels indépendants (certains partenaires peuvent rémunérer le site via affiliation sans impact sur votre tarif).</p>
        </div>

        <div class="cta-strip">
          <div>
            <h3>Besoin d'un outillage Factur-X 100 % local sans abonnement mensuel ?</h3>
            <p>FacturKit 2027 réunit classeur Excel pilotage TVA/URSSAF (<strong>19 €</strong>), Studio Factur-X EN 16931 hors-ligne (<strong>49 €</strong>), Suite Pro + workflows n8n (<strong>119 €</strong>) ou le Cockpit Conformité Bilingue FR+EN sur Gumroad (<strong>79 €</strong>).</p>
          </div>
          <div class="cta-actions">
            <a class="btn-light" href="{STRIPE_SLOT1}" target="_blank" rel="noopener">Pack Pilotage 19 €</a>
            <a class="btn-accent-solid" href="{STRIPE_SLOT2}" target="_blank" rel="noopener">Studio Factur-X 49 €</a>
            <a class="btn-light" href="{STRIPE_SLOT3}" target="_blank" rel="noopener">Suite Pro 119 €</a>
            <a class="btn-light" href="{GUMROAD_HFXUUZ}" target="_blank" rel="noopener">Cockpit Gumroad 79 €</a>
          </div>
        </div>

        <div style="margin-top:34px;">
          <h2>Questions fréquentes — {title_h} (NAF {naf_h})</h2>
{faq_html}
        </div>

        <div style="margin-top:34px;">
          <h2>Autres fiches métiers &amp; codes NAF proches</h2>
          <div class="sibling-grid">
{sib_html}
          </div>
        </div>
      </div>
    </section>
  </main>

{render_footer("../")}
  <script src="../pa-affiliates.js"></script>
</body>
</html>
"""


def build_directory_page() -> str:
    sectors = sorted({p["sector"] for p in PROFESSIONS})
    url = f"{SITE_BASE}/metiers/"
    json_ld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "CollectionPage",
                "name": "Annuaire Factur-X 2026–2027 par Métier & Code NAF (50 Fiches)",
                "url": url,
                "inLanguage": "fr-FR",
                "numberOfItems": len(PROFESSIONS),
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "FacturKit 2027", "item": f"{SITE_BASE}/"},
                    {"@type": "ListItem", "position": 2, "name": "50 Métiers & Codes NAF", "item": url},
                ],
            },
        ],
    }

    pills = ['<button class="dir-pill" type="button" data-sector="all" aria-pressed="true">Tous (50)</button>']
    for sec in sectors:
        cnt = sum(1 for p in PROFESSIONS if p["sector"] == sec)
        pills.append(
            f'<button class="dir-pill" type="button" data-sector="{html.escape(sec)}" aria-pressed="false">{html.escape(sec)} ({cnt})</button>'
        )

    cards = []
    for p in PROFESSIONS:
        haystack = f"{p['title']} {p['short']} {p['naf']} {p['sector']} {p['tva']}".lower()
        cards.append(
            f"""          <a class="metier-card" href="./{p['slug']}.html" data-sector="{html.escape(p['sector'])}" data-search="{html.escape(haystack)}">
            <div class="naf-pill" style="margin-bottom:8px;">NAF {html.escape(p['naf'])} · {html.escape(p['sector'])}</div>
            <h2 style="font-size:1.05rem;margin:0 0 6px;">{html.escape(p['title'])}</h2>
            <p style="font-size:0.86rem;color:var(--muted);margin:0;">{html.escape(p['flux'])}</p>
          </a>"""
        )

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Factur-X 2026–2027 par Métier &amp; Code NAF — 50 Guides Pratiques | FacturKit</title>
  <meta name="description" content="50 fiches pratiques Facturation Électronique 2026–2027 par métier et code NAF : réception 01/09/2026, émission Factur-X 1.09.2 au 01/09/2027, règles TVA/e-reporting et choix de Plateforme Agréée.">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{url}">
  <link rel="icon" type="image/svg+xml" href="../favicon.svg">
  <script type="application/ld+json">
{json.dumps(json_ld, ensure_ascii=False, indent=2)}
  </script>
  <link rel="stylesheet" href="../styles.css">
  <style>{SHARED_STYLE}</style>
</head>
<body>
{render_header("../")}

  <main>
    <section class="metier-hero">
      <div class="container">
        <div class="breadcrumb"><a href="../index.html">FacturKit 2027</a> › 50 Métiers &amp; Codes NAF</div>
        <div class="naf-pill">Annuaire pSEO 2026–2027 · 50 Codes NAF couverts · 159 PA DGFiP</div>
        <h1>Facture électronique &amp; Factur-X 2026–2027 par métier (50 fiches NAF)</h1>
        <p class="hero-lead">
          Trouvez les obligations exactes de votre secteur (autoliquidation BTP, exonération santé/formation, e-reporting B2C/export, acomptes, notes d'honoraires) et la Plateforme Agréée la mieux adaptée à votre profil.
        </p>
        <div class="hero-cta-row">
          <a href="../comparateur-pa-2026.html" class="btn-primary">Ouvrir le Comparateur PA 2026</a>
          <a href="../simulateur-statut-urssaf-2026.html" class="btn-outline">Simulateur URSSAF &amp; Statut 2026</a>
          <a href="../audit-facture-gratuit.html?mode=fx" class="btn-outline">Inspecteur Factur-X Gratuit</a>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="dir-controls">
          <input id="metier-search" class="dir-search" type="search" placeholder="Filtrer par métier ou code NAF (ex. 62.01Z, plombier, médecin, e-commerce)..." aria-label="Rechercher un métier ou code NAF">
          <div style="display:flex;flex-wrap:wrap;gap:8px;">
            {" ".join(pills)}
          </div>
        </div>
        <p id="dir-count" style="font-size:0.88rem;color:var(--muted);margin:0 0 14px;">50 / 50 fiches métiers affichées</p>

        <div id="metier-list" class="metier-grid">
{chr(10).join(cards)}
        </div>
      </div>
    </section>
  </main>

{render_footer("../")}
  <script>
  (function () {{
    var search = document.getElementById("metier-search");
    var pills = document.querySelectorAll(".dir-pill");
    var cards = document.querySelectorAll("#metier-list .metier-card");
    var count = document.getElementById("dir-count");
    var activeSector = "all";

    function update() {{
      var q = (search && search.value ? search.value : "").trim().toLowerCase();
      var visible = 0;
      for (var i = 0; i < cards.length; i++) {{
        var c = cards[i];
        var sec = c.getAttribute("data-sector");
        var hay = c.getAttribute("data-search") || "";
        var ok = (activeSector === "all" || sec === activeSector) && (!q || hay.indexOf(q) !== -1);
        c.hidden = !ok;
        if (ok) visible++;
      }}
      if (count) count.textContent = visible + " / " + cards.length + " fiches métiers affichées";
    }}

    if (search) search.addEventListener("input", update);
    for (var j = 0; j < pills.length; j++) {{
      pills[j].addEventListener("click", function (ev) {{
        var btn = ev.currentTarget;
        activeSector = btn.getAttribute("data-sector") || "all";
        for (var k = 0; k < pills.length; k++) {{
          pills[k].setAttribute("aria-pressed", pills[k] === btn ? "true" : "false");
        }}
        update();
      }});
    }}
  }})();
  </script>
</body>
</html>
"""


def update_sitemap(repo_root: Path) -> int:
    core_urls = [
        (f"{SITE_BASE}/", "2026-11-21", "weekly", "1.0"),
        (f"{SITE_BASE}/en.html", "2026-11-20", "weekly", "0.95"),
        (f"{SITE_BASE}/audit-facture-gratuit.html", "2026-11-21", "weekly", "0.9"),
        (f"{SITE_BASE}/comparateur-pa-2026.html", "2026-11-21", "weekly", "0.9"),
        (f"{SITE_BASE}/simulateur-statut-urssaf-2026.html", LASTMOD, "weekly", "0.9"),
        (f"{SITE_BASE}/metiers/", LASTMOD, "weekly", "0.9"),
        (f"{SITE_BASE}/guides/lire-verifier-facture-factur-x-recue-2026.html", "2026-11-20", "monthly", "0.85"),
        (f"{SITE_BASE}/guides/mentions-obligatoires-facture-2026-2027.html", "2026-11-20", "monthly", "0.8"),
        (f"{SITE_BASE}/guides/generer-factur-x-sans-abonnement-micro-entreprise.html", "2026-11-20", "monthly", "0.8"),
        (f"{SITE_BASE}/guides/comparatif-plateformes-agreees-pa-pdp-2027.html", "2026-11-20", "monthly", "0.8"),
        (f"{SITE_BASE}/guides/facture-electronique-micro-entreprise-2027.html", "2026-11-20", "monthly", "0.8"),
        (f"{SITE_BASE}/guides/franchise-tva-293b-factur-x.html", "2026-11-17", "monthly", "0.8"),
        (f"{SITE_BASE}/guides/erreurs-calcul-totaux-en16931-br-co.html", "2026-11-17", "monthly", "0.8"),
        (f"{SITE_BASE}/guides/checklist-reforme-facturation-electronique-tpe.html", "2026-11-20", "monthly", "0.8"),
    ]
    for p in PROFESSIONS:
        core_urls.append((f"{SITE_BASE}/metiers/{p['slug']}.html", LASTMOD, "monthly", "0.75"))

    entries = []
    for loc, mod, freq, prio in core_urls:
        entries.append(
            f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{mod}</lastmod>\n    <changefreq>{freq}</changefreq>\n    <priority>{prio}</priority>\n  </url>"
        )
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(entries) + "\n</urlset>\n"
    (repo_root / "sitemap.xml").write_text(xml, encoding="utf-8")
    return len(core_urls)


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    out_dir = repo_root / "metiers"
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "index.html").write_text(build_directory_page(), encoding="utf-8")

    for idx, prof in enumerate(PROFESSIONS):
        # Pick 4 related/sibling professions deterministically
        same_sector = [p for p in PROFESSIONS if p["sector"] == prof["sector"] and p["slug"] != prof["slug"]]
        others = [p for p in PROFESSIONS if p["slug"] != prof["slug"] and p not in same_sector]
        siblings = (same_sector + others[idx % max(1, len(others)):] + others)[:4]
        (out_dir / f"{prof['slug']}.html").write_text(
            build_profession_page(prof, siblings), encoding="utf-8"
        )

    total_urls = update_sitemap(repo_root)
    print(f"Generated {len(PROFESSIONS)} profession pages + metiers/index.html; sitemap.xml updated ({total_urls} URLs).")


if __name__ == "__main__":
    main()
