/* ============================================================================
   Carvex XLS — configuração da página de vendas
   Edite este arquivo para ligar os botões de compra. Nada mais precisa mudar.
   ============================================================================ */
window.CARVEX_CONFIG = {
  brand: "Carvex XLS",

  // Contato (opcional). WhatsApp: só números com DDI + DDD, ex.: "5511999999999"
  whatsapp: "5591981902529",
  email: "",
  instagram: "",

  // Mostrar o preço promocional como preço atual (e o individual riscado)
  showPromo: true,

  // Dias de garantia exibidos na página (direito de arrependimento: 7 dias no CDC, art. 49)
  guaranteeDays: 7,

  // Link de pagamento (Hotmart, Kiwify, Eduzz, Mercado Pago, Stripe...) de cada produto e kit.
  // Se deixar vazio, o botão abre o WhatsApp (se configurado) ou avisa que a compra está em breve.
  checkout: {
    "fluxo-de-caixa": "",
    "precificador": "",
    "estoque-inteligente": "",
    "contas-pagar-receber": "",
    "crm-funil": "",
    "dre-ponto-equilibrio": "",
    "ficha-tecnica-cmv": "",
    "ordem-de-servico": "",
    "controle-de-obras": "",
    "agenda-retornos": "",

    "kit-pequeno-empresario": "",
    "kit-loja": "",
    "kit-restaurante": "",
    "kit-oficina": "",
    "kit-construtora": "",
    "kit-clinica": "",
    "kit-comercial-e-servicos": "",
    "kit-completo": ""
  }
};
