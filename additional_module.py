# ==================================================================
# FULL RECONCILIATION BASED ON VOLUME INSPECTION
# ==================================================================

def reconcile_from_volume_inspection(day_inspect, Jb_visual_percent, 
                                    D_eff_inspect, ball_mass_initial, 
                                    total_addition, total_tonnage):
    """
    Reconcile wear rate berdasarkan inspeksi visual volume bola
    
    Parameters:
    -----------
    day_inspect : int
        Hari inspeksi (biasanya saat reline, day 180 atau major stop)
    Jb_visual_percent : float
        Persentase volume bola hasil inspeksi visual (misal: 0.14 = 14%)
        Ini adalah estimasi operator/engineer saat mill dibuka
    D_eff_inspect : float
        Diameter efektif saat inspeksi (m) - dari pengukuran liner
    ball_mass_initial : float
        Massa bola awal campaign (ton)
    total_addition : float
        Total penambahan bola selama campaign (ton)
    total_tonnage : float
        Total tonnase yang diproses (ton)
    
    Returns:
    --------
    wear_rate_reconciled : float
        Wear rate hasil rekonsiliasi (kg/ton)
    ball_mass_reconciled : float
        Massa bola hasil rekonsiliasi (ton)
    """
    
    # 1. Hitung volume mill efektif saat inspeksi
    V_eff_inspect = math.pi/4 * D_eff_inspect**2 * L
    
    # 2. Konversi Jb visual ke massa bola
    # Formula: m_ball = Jb × V × (1-ε) × ρ_ball
    ball_mass_reconciled = Jb_visual_percent * V_eff_inspect * (1 - E) * Rhoball
    
    # 3. Hitung total wear dari neraca massa
    total_wear = ball_mass_initial + total_addition - ball_mass_reconciled
    
    # 4. Hitung wear rate rata-rata campaign
    wear_rate_reconciled = total_wear / total_tonnage * 1000  # kg/ton
    
    # 5. Diagnostik lengkap
    print("="*60)
    print(f"FULL RECONCILIATION AT DAY {day_inspect}")
    print("="*60)
    print(f"\nVISUAL INSPECTION:")
    print(f"  Jb visual estimate:         {Jb_visual_percent:.1%} ({Jb_visual_percent:.4f})")
    print(f"  Diameter effective:         {D_eff_inspect:.4f} m")
    print(f"  Volume effective:           {V_eff_inspect:.2f} m³")
    
    print(f"\nBACK-CALCULATED MASS:")
    print(f"  Ball mass (from visual):    {ball_mass_reconciled:.2f} tonnes")
    
    print(f"\nMASS BALANCE:")
    print(f"  Ball mass initial:          {ball_mass_initial:.2f} tonnes")
    print(f"  Total addition:             {total_addition:.2f} tonnes")
    print(f"  Ball mass final (visual):   {ball_mass_reconciled:.2f} tonnes")
    print(f"  ───────────────────────────────────────────────")
    print(f"  Total wear (calculated):    {total_wear:.2f} tonnes")
    
    print(f"\nWEAR RATE RECONCILIATION:")
    print(f"  Total tonnage processed:    {total_tonnage/1e6:.3f} Mt")
    print(f"  Reconciled wear rate:       {wear_rate_reconciled:.3f} kg/ton")
    
    print("="*60)
    
    return wear_rate_reconciled, ball_mass_reconciled, total_wear


# ==================================================================
# EXAMPLE: RELINE AT DAY 180
# ==================================================================

# Saat mill dibuka untuk reline, engineer melakukan inspeksi visual
# Contoh: "Kelihatannya bola cuma mengisi sekitar 14% dari volume mill"

Jb_visual_reline = 0.14  # 14% dari volume mill (visual estimate)

# Ukur liner thickness aktual dengan ultrasonic gauge
# Misalnya ternyata liner thickness = 75 mm (bukan 80 mm seperti asumsi)
liner_thickness_actual = 75  # mm

# Hitung diameter efektif aktual
D_eff_actual = D0 + 2 * (200 - liner_thickness_actual) / 1000

print(f"\nLINER MEASUREMENT AT RELINE:")
print(f"  Assumed liner thickness:    {plate[-1]:.1f} mm")
print(f"  Actual liner thickness:     {liner_thickness_actual:.1f} mm")
print(f"  Difference:                 {liner_thickness_actual - plate[-1]:.1f} mm")
print(f"\n  Assumed diameter:           {D_eff[-1]:.4f} m")
print(f"  Actual diameter:            {D_eff_actual:.4f} m")
print(f"  Difference:                 {(D_eff_actual - D_eff[-1])*1000:.2f} mm\n")

# Lakukan rekonsiliasi
wear_reconciled, ball_mass_final_actual, total_wear_actual = reconcile_from_volume_inspection(
    day_inspect=180,
    Jb_visual_percent=Jb_visual_reline,
    D_eff_inspect=D_eff_actual,
    ball_mass_initial=ball_mass0,
    total_addition=np.sum(ball_add),
    total_tonnage=np.sum(ton_daily)
)

# ==================================================================
# COMPARISON: ESTIMATED vs ACTUAL
# ==================================================================

# Dari simulasi prediktif
ball_mass_predicted = Jb_pred[-1] * V_eff[-1] * (1 - E) * Rhoball
Jb_predicted = Jb_pred[-1]

# Dari visual inspection dengan diameter terkoreksi
V_eff_actual = math.pi/4 * D_eff_actual**2 * L

print(f"\n{'='*60}")
print("COMPARISON: PREDICTED vs ACTUAL")
print("="*60)
print(f"\nJb COMPARISON:")
print(f"  Predicted (from model):     {Jb_predicted:.4f}")
print(f"  Actual (visual):            {Jb_visual_reline:.4f}")
print(f"  Deviation:                  {Jb_visual_reline - Jb_predicted:+.4f}")
print(f"  Deviation (%):              {(Jb_visual_reline/Jb_predicted - 1)*100:+.2f}%")

print(f"\nBALL MASS COMPARISON:")
print(f"  Predicted (from model):     {ball_mass_predicted:.2f} tonnes")
print(f"  Actual (from visual):       {ball_mass_final_actual:.2f} tonnes")
print(f"  Deviation:                  {ball_mass_final_actual - ball_mass_predicted:+.2f} tonnes")

print(f"\nWEAR RATE COMPARISON:")
print(f"  Estimated (controller):     {ctrl.wear:.3f} kg/ton")
print(f"  Reconciled (actual):        {wear_reconciled:.3f} kg/ton")
print(f"  Deviation:                  {wear_reconciled - ctrl.wear:+.3f} kg/ton")
print(f"  Deviation (%):              {(wear_reconciled/ctrl.wear - 1)*100:+.2f}%")

print(f"\nVOLUME COMPARISON:")
print(f"  Assumed volume (worn):      {V_eff[-1]:.2f} m³")
print(f"  Actual volume (measured):   {V_eff_actual:.2f} m³")
print(f"  Deviation:                  {V_eff_actual - V_eff[-1]:+.2f} m³")

print("="*60)


# ==================================================================
# INITIALIZE NEXT CAMPAIGN with RECONCILED DATA
# ==================================================================

def initialize_next_campaign(wear_rate_reconciled, Jb_target=0.15):
    """
    Initialize controller untuk campaign berikutnya dengan data rekonsiliasi
    """
    
    # Volume mill setelah reline (diameter kembali ke D0)
    V0_new = math.pi/4 * D0**2 * L
    
    # Hitung massa bola target untuk campaign baru
    ball_mass_target = Jb_target * V0_new * (1 - E) * Rhoball
    
    # Controller baru dengan wear rate terkoreksi
    ctrl_new = Controller()
    ctrl_new.wear = wear_rate_reconciled  # Gunakan wear rate hasil rekonsiliasi
    ctrl_new.jb_est = Jb_target
    ctrl_new.mass0 = ball_mass_target
    ctrl_new.total_add = 0.0
    ctrl_new.total_ton = 0.0
    
    print(f"\n{'='*60}")
    print("NEXT CAMPAIGN INITIALIZATION")
    print("="*60)
    print(f"Wear rate (from reconciliation): {wear_rate_reconciled:.3f} kg/ton")
    print(f"Target Jb:                       {Jb_target:.4f}")
    print(f"Volume (new liner):              {V0_new:.2f} m³")
    print(f"Target ball mass:                {ball_mass_target:.2f} tonnes")
    print("="*60)
    
    return ctrl_new, ball_mass_target


# Initialize controller untuk campaign berikutnya
ctrl_next_campaign, ball_mass_next = initialize_next_campaign(
    wear_rate_reconciled=wear_reconciled,
    Jb_target=0.15
)



# ==================================================================
# UNCERTAINTY ANALYSIS for VISUAL INSPECTION
# ==================================================================

def visual_inspection_uncertainty(Jb_visual, uncertainty_percent=10):
    """
    Analisis sensitivitas terhadap uncertainty inspeksi visual
    
    Parameters:
    -----------
    Jb_visual : float
        Jb hasil inspeksi visual (misal: 0.14)
    uncertainty_percent : float
        Uncertainty estimasi visual (default: ±10%)
    
    Returns:
    --------
    Jb_low, Jb_high : float
        Range Jb dengan confidence interval
    """
    
    # Range Jb
    delta = Jb_visual * (uncertainty_percent / 100)
    Jb_low = Jb_visual - delta
    Jb_high = Jb_visual + delta
    
    # Hitung impact pada wear rate
    V_eff = math.pi/4 * D_eff_actual**2 * L
    
    ball_mass_low = Jb_low * V_eff * (1 - E) * Rhoball
    ball_mass_high = Jb_high * V_eff * (1 - E) * Rhoball
    
    wear_low = (ball_mass0 + np.sum(ball_add) - ball_mass_high) / np.sum(ton_daily) * 1000
    wear_high = (ball_mass0 + np.sum(ball_add) - ball_mass_low) / np.sum(ton_daily) * 1000
    
    print(f"\n{'='*60}")
    print(f"VISUAL INSPECTION UNCERTAINTY (±{uncertainty_percent}%)")
    print("="*60)
    print(f"Jb visual estimate:         {Jb_visual:.4f}")
    print(f"Jb range:                   {Jb_low:.4f} - {Jb_high:.4f}")
    print(f"\nBall mass range:            {ball_mass_low:.2f} - {ball_mass_high:.2f} tonnes")
    print(f"Wear rate range:            {wear_low:.3f} - {wear_high:.3f} kg/ton")
    print(f"\nRecommendation: Use mid-point {wear_reconciled:.3f} kg/ton")
    print(f"with ±{abs(wear_high - wear_reconciled):.3f} kg/ton uncertainty")
    print("="*60)
    
    return Jb_low, Jb_high, wear_low, wear_high


# Analisis uncertainty
Jb_low, Jb_high, wear_low, wear_high = visual_inspection_uncertainty(
    Jb_visual=Jb_visual_reline,
    uncertainty_percent=10  # ±10% adalah typical untuk visual estimate
)
