package com.example.fraudbackend;

public class FraudPredictionRequest {
    private float transactionAmt;
    private float card1;
    private float pEmaildomainFreq;
    private float card4Freq;
    private float productCdFreq;
    private float amtZScoreCard1;
    private float cardTxCount24h;

    // Getters and Setters
    public float getTransactionAmt() { return transactionAmt; }
    public void setTransactionAmt(float transactionAmt) { this.transactionAmt = transactionAmt; }

    public float getCard1() { return card1; }
    public void setCard1(float card1) { this.card1 = card1; }

    public float getpEmaildomainFreq() { return pEmaildomainFreq; }
    public void setpEmaildomainFreq(float pEmaildomainFreq) { this.pEmaildomainFreq = pEmaildomainFreq; }

    public float getCard4Freq() { return card4Freq; }
    public void setCard4Freq(float card4Freq) { this.card4Freq = card4Freq; }

    public float getProductCdFreq() { return productCdFreq; }
    public void setProductCdFreq(float productCdFreq) { this.productCdFreq = productCdFreq; }

    public float getAmtZScoreCard1() { return amtZScoreCard1; }
    public void setAmtZScoreCard1(float amtZScoreCard1) { this.amtZScoreCard1 = amtZScoreCard1; }

    public float getCardTxCount24h() { return cardTxCount24h; }
    public void setCardTxCount24h(float cardTxCount24h) { this.cardTxCount24h = cardTxCount24h; }

    public float[] toFloatArray() {
        return new float[]{
            transactionAmt, card1, pEmaildomainFreq, card4Freq, 
            productCdFreq, amtZScoreCard1, cardTxCount24h
        };
    }
}
