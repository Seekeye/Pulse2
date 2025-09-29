// Vercel Serverless Function
export default async function handler(req, res) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    // Simular datos de precios (puedes conectar con APIs reales)
    const prices = {
      "BTC-USD": 111950.015,
      "ETH-USD": 4096.385,
      "ADA-USD": 0.7905,
      "MATIC-USD": 0.3794,
      "SOL-USD": 206.07,
      "LINK-USD": 21.09
    };

    res.status(200).json({ prices });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
}
