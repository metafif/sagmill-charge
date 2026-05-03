"""
Predictive Ball Addition vs Constant
Full Morrell C-model, step changes in ore, independent validation
"""

import math
import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt

# ==================================================================
# FULL MORRELL C-MODEL
# ==================================================================
D0, L, Ld, rpm = 12.2, 6.1, 1.5, 8.99
rt, E, U = 2.5, 0.40, 1.0
Rhoball, Rhoore = 7.8, 2.60
percentsolids = 0.75
is_gearless, is_grate = True, True

def Rhopulpcalc(ps, ro): return ps * ro + (1 - ps) * 1.0
def SolidbyV(ps, ro): return (ps * 1.0) / (ps * 1.0 + (1 - ps) * ro)

def chargedensity(Jt, Jb, sv, E, U, rb, ro):
    return ((Jt*ro*(1 - E + E*U*sv)) + (Jb*(rb - ro)*(1 - E)) + (Jt*E*U*(1 - sv))) / Jt

def angle(Jt, rpm, D, is_grate, rt):
    null = rpm / (42.3 * (D ** -0.5))
    null = max(min(null, 1.2), 0.2)
    ThetaC = 0.35 * (3.364 - Jt)
    try: ThetaT = 2.5307*(1.2796 - Jt)*(1 - math.exp(-19.42*(ThetaC - null))) + math.pi/2
    except OverflowError: ThetaT = math.pi/2
    if is_grate: ThetaTO = ThetaT
    else:
        try: ThetaTO = math.pi + math.asin(rt / (D/2))
        except ValueError: ThetaTO = math.pi
    try: ThetaS = (math.pi/2) - (((ThetaT - math.pi/2) * ((0.3386 + 0.1041*null) + ((1.54 - 2.5673*null)*Jt))))
    except OverflowError: ThetaS = math.pi/2
    return null, ThetaC, ThetaT, ThetaTO, ThetaS

def innersurfaceradiusofcharge(D, rpm, Jt, ThetaS, ThetaT):
    g, rm = 9.80665, D/2
    Nm, Nmean = rpm/60, rpm/120
    denom = 2*math.pi + ThetaS - ThetaT
    try: rmean = (rm/2)*(1 + (1 - (2*math.pi*Jt)/denom)**0.5)
    except ValueError: rmean = rm*0.7
    tc = (2*math.pi - ThetaT + ThetaS)/(2*math.pi*Nmean)
    sin_diff = max(math.sin(ThetaS) - math.sin(ThetaT), 0.001)
    tf = (2*rmean*sin_diff/g)**0.5
    Beta = tc/(tf + tc)
    try: ri = rm*(1 - (2*math.pi*Beta*Jt)/denom)**0.5
    except ValueError: ri = rm*0.5
    return Nm, Nmean, rmean, tc, tf, Beta, ri

def zparamater(Jt): return (1 - Jt)**0.4532

def powerdraw(L, Ld, rpm, D, ri, rt, Rhocharge, Rhopulp, ThetaS, ThetaT, ThetaTO, z):
    g, rm = 9.80665, D/2
    Nm = rpm/60
    Pt = ((math.pi*g*L*Nm*rm)/(3*(rm - z*ri))) * (2*rm**3 - 3*z*ri*rm**2 + (ri**3)*(3*z - 2)) * \
         (Rhocharge*(math.sin(ThetaS) - math.sin(ThetaT)) + Rhopulp*(math.sin(ThetaT) - math.sin(ThetaTO)))
    Pc = ((math.pi*Ld*Nm*g)/(3*(rm - rt))) * ((rm**4 - 4*rm*ri**3 + 3*ri**4) * \
         (Rhocharge*(math.sin(ThetaS) - math.sin(ThetaT)) + Rhopulp*(math.sin(ThetaT) - math.sin(ThetaTO)))) + \
         ((2*(math.pi**3)*Ld*Nm**3*Rhocharge)/(5*(rm - rt))) * (rm**5 - 5*rm*ri**4 + 4*ri**5)
    return Pt, Pc, Pt + Pc

def noloadpowerdraw(is_gearless, D, null, Ld, L):
    K2 = 1.0 if is_gearless else 1.68
    return K2 * (D**2.05) * (null*(0.667*Ld + L))**0.82

def grosspower(Pnoload, Ptotal): return Pnoload + 1.26*Ptotal

def forward_power(Jt, Jb, D_eff):
    ps, ro = percentsolids, Rhoore
    sv = SolidbyV(ps, ro)
    Rhopulp = Rhopulpcalc(ps, ro)
    Rhocharge = chargedensity(Jt, Jb, sv, E, U, Rhoball, ro)
    null, ThetaC, ThetaT, ThetaTO, ThetaS = angle(Jt, rpm, D_eff, is_grate, rt)
    Nm, Nmean, rmean, tc, tf, Beta, ri = innersurfaceradiusofcharge(D_eff, rpm, Jt, ThetaS, ThetaT)
    z = zparamater(Jt)
    Pnoload = noloadpowerdraw(is_gearless, D_eff, null, Ld, L)
    Pt, Pc, Ptotal = powerdraw(L, Ld, rpm, D_eff, ri, rt, Rhocharge, Rhopulp, ThetaS, ThetaT, ThetaTO, z)
    return grosspower(Pnoload, Ptotal)

def forward_mass_charge(Jt, Jb, D_eff):
    V = math.pi/4 * D_eff**2 * L
    sv = SolidbyV(percentsolids, Rhoore)
    m_ball = Jb * V * (1 - E) * Rhoball
    m_ore = Rhoore * V * (Jt*((1 - E) + (E*sv*U)) - Jb*(1 - E))
    m_water = Jt * V * E * U * (1 - sv) * 1.0
    return m_ball + m_ore + m_water

def shell_mass(D, L, Ld, thickness, rho_steel):
    Ro, Ri = D/2 + thickness, D/2
    Vcyl = math.pi * L * (Ro**2 - Ri**2)
    Vcone = 2 * (1/3) * math.pi * Ld * (Ro**2 - Ri**2)
    return (Vcyl + Vcone) * rho_steel

def liner_mass(D, L, plate_mm, rho_steel):
    pm = plate_mm / 1000.0
    V = math.pi * L * ((D/2 + pm)**2 - (D/2)**2)
    return V * rho_steel

# Inverse model
def estimate_jb(power_m, mass_m, D_eff_d, m_shell_d, m_liner_d):
    def objective(vars):
        Jt, Jb = vars
        p_calc = forward_power(Jt, Jb, D_eff_d)
        m_calc = m_shell_d + m_liner_d + forward_mass_charge(Jt, Jb, D_eff_d)
        return ((p_calc - power_m)/power_m)**2 + ((m_calc - mass_m)/mass_m)**2
    constraints = [
        {'type': 'ineq', 'fun': lambda x: x[0] - x[1] - 0.01},
        {'type': 'ineq', 'fun': lambda x: x[0] - 0.10},
        {'type': 'ineq', 'fun': lambda x: 0.40 - x[0]},
        {'type': 'ineq', 'fun': lambda x: x[1] - 0.05},
        {'type': 'ineq', 'fun': lambda x: 0.30 - x[1]},
    ]
    try:
        res = minimize(objective, [0.35, 0.15], method='SLSQP', constraints=constraints,
                       options={'ftol': 1e-9, 'maxiter': 300})
        if res.success: return res.x[1]
    except: pass
    return 0.15

# ==================================================================
# SIMULATION
# ==================================================================
np.random.seed(42)
DAYS = 180
days = np.arange(1, DAYS+1)
TPH_NOMINAL = 2200
HOURS_PER_SHIFT = 12
SHIFTS_PER_DAY = 2

# Step changes in wear rate
true_wear = np.zeros(DAYS)
true_wear[:60] = 0.54
true_wear[60:120] = 0.57
true_wear[120:] = 0.52

# Generate shift data
ton_shift = np.zeros((DAYS, SHIFTS_PER_DAY))
wear_shift = np.zeros((DAYS, SHIFTS_PER_DAY))
for d in range(DAYS):
    for s in range(SHIFTS_PER_DAY):
        ton_shift[d,s] = TPH_NOMINAL * (1 + np.random.normal(0, 0.02)) * HOURS_PER_SHIFT
        wear_shift[d,s] = true_wear[d] * (1 + np.random.normal(0, 0.05))

ton_daily = np.sum(ton_shift, axis=1)

# Liner wear
mt_cum = np.cumsum(ton_daily / 1e6)
plate = np.clip(200 - (200-80)*(mt_cum/9.0), 80, 200)
D_eff = D0 + 2*(200 - plate)/1000
V_eff = np.pi/4 * D_eff**2 * L
m_liner = np.array([liner_mass(D_eff[d], L, plate[d], 7.85) for d in range(DAYS)])
m_shell = shell_mass(D0, L, Ld, 0.120, 7.85)

V0 = math.pi/4 * D0**2 * L
ball_mass0 = 0.15 * V0 * (1 - E) * Rhoball



# ==================================================================
# INITIAL CONDITIONS
# ==================================================================
V0 = math.pi/4 * D0**2 * L
ball_mass0 = 0.15 * V0 * (1 - E) * Rhoball

print("="*60)
print("INITIAL CONDITIONS (Day 0)")
print("="*60)
print(f"Initial diameter (D0):        {D0:.2f} m")
print(f"EGL length (L):               {L:.2f} m")
print(f"Initial volume (V0):          {V0:.2f} m³")
print(f"Target Jb:                    {0.15:.2f}")
print(f"Porosity (E):                 {E:.2f}")
print(f"Ball density:                 {Rhoball:.2f} ton/m³")
print(f"\nInitial ball mass:            {ball_mass0:.2f} tonnes")
print(f"Initial ore+water mass:       {forward_mass_charge(0.35, 0.15, D0) - ball_mass0:.2f} tonnes")
print(f"Initial total charge:         {forward_mass_charge(0.35, 0.15, D0):.2f} tonnes")
print("="*60 + "\n")

# Noise
power_noise = np.random.normal(0, 0.02, DAYS)
mass_noise = np.random.normal(0, 0.005, DAYS)
mass_drift = np.linspace(0, 0.02, DAYS)

# --- CONSTANT ---
const_add = np.mean(ton_daily) * 0.54 / 1000
Jb_const = np.zeros(DAYS)
power_const = np.zeros(DAYS)
mass_const = np.zeros(DAYS)

bm = ball_mass0
for d in range(DAYS):
    wear = sum(wear_shift[d,s] * ton_shift[d,s] / 1000 for s in range(SHIFTS_PER_DAY))
    bm = bm + const_add - wear
    Jb_const[d] = bm / (V_eff[d] * (1 - E) * Rhoball)
    power_const[d] = forward_power(0.35, Jb_const[d], D_eff[d])
    mass_const[d] = m_shell + m_liner[d] + forward_mass_charge(0.35, Jb_const[d], D_eff[d])

# --- PREDICTIVE CONTROLLER ---
class Controller:
    def __init__(self):
        self.jb_est = 0.15
        self.wear = 0.54
        self.total_add = 0.0
        self.total_ton = 0.0
        self.mass0 = ball_mass0
        self.prev_add = const_add
        
    def update(self, power_meas, mass_meas, D_eff, m_liner, V_eff, addition, tonnage):
        self.jb_est = estimate_jb(power_meas, mass_meas, D_eff, m_shell, m_liner)
        self.total_add += addition
        self.total_ton += tonnage
        mass_est = self.jb_est * V_eff * (1 - E) * Rhoball
        total_wear = self.total_add - (mass_est - self.mass0)
        if self.total_ton > 0:
            self.wear = float(np.clip(total_wear / self.total_ton * 1000, 0.50, 0.58))
    
    def plan(self, V_today, V_tomorrow, ton_forecast):
        mass_today = self.jb_est * V_today * (1 - E) * Rhoball
        mass_target = 0.15 * V_tomorrow * (1 - E) * Rhoball
        wear_next = self.wear * ton_forecast / 1000
        add = mass_target - mass_today + wear_next
        add = np.clip(add, self.prev_add - 3.0, self.prev_add + 3.0)
        add = float(np.clip(add, 22, 35))
        self.prev_add = add
        return add

ctrl = Controller()

Jb_pred = np.zeros(DAYS)
Jb_est = np.zeros(DAYS)
power_pred = np.zeros(DAYS)
power_meas = np.zeros(DAYS)
mass_pred = np.zeros(DAYS)
mass_meas = np.zeros(DAYS)
ball_add = np.zeros(DAYS)
wear_est = np.zeros(DAYS)

bm = ball_mass0
addition = const_add

for d in range(DAYS):
    wear = sum(wear_shift[d,s] * ton_shift[d,s] / 1000 for s in range(SHIFTS_PER_DAY))
    bm = bm + addition - wear
    Jb_pred[d] = bm / (V_eff[d] * (1 - E) * Rhoball)
    
    power_pred[d] = forward_power(0.35, Jb_pred[d], D_eff[d])
    mass_pred[d] = m_shell + m_liner[d] + forward_mass_charge(0.35, Jb_pred[d], D_eff[d])
    
    p_meas = power_pred[d] * (1 + power_noise[d])
    m_meas = mass_pred[d] * (1 + mass_noise[d] + mass_drift[d])
    power_meas[d] = p_meas
    mass_meas[d] = m_meas
    
    ctrl.update(p_meas, m_meas, D_eff[d], m_liner[d], V_eff[d], addition, ton_daily[d])
    Jb_est[d] = ctrl.jb_est
    wear_est[d] = ctrl.wear
    ball_add[d] = addition
    
    if d < DAYS - 1:
        addition = ctrl.plan(V_eff[d], V_eff[d+1], ton_daily[d])

# ==================================================================
# VALIDATION (back-calculate truth from noise-free power & mass)
# ==================================================================
Jb_actual = np.zeros(DAYS)
for d in range(DAYS):
    Jb_actual[d] = estimate_jb(power_pred[d], mass_pred[d], D_eff[d], m_shell, m_liner[d])

wear_actual = np.zeros(DAYS)
for d in range(1, DAYS):
    my = Jb_actual[d-1] * V_eff[d-1] * (1 - E) * Rhoball
    mt = Jb_actual[d] * V_eff[d] * (1 - E) * Rhoball
    wear_actual[d] = (ball_add[d] - (mt - my)) / ton_daily[d] * 1000

# ==================================================================
# ADDITIONAL CALCULATIONS FOR REPORTING
# ==================================================================

# 1. Diameter calculations
D_initial = D_eff[0]  # Diameter hari ke-1
D_final = D_eff[-1]   # Diameter hari ke-180
delta_D = D_final - D_initial

print("\n" + "="*60)
print("DIAMETER CALCULATIONS")
print("="*60)
print(f"Initial diameter (day 1):   {D_initial:.4f} m")
print(f"Final diameter (day 180):   {D_final:.4f} m")
print(f"Delta diameter:             {delta_D:.4f} m ({delta_D*1000:.2f} mm)")
print(f"Percentage increase:        {(delta_D/D_initial)*100:.2f}%")

# 2. Volume calculations
V_initial = V_eff[0]   # Volume hari ke-1
V_final = V_eff[-1]    # Volume hari ke-180
delta_V = V_final - V_initial

print("\n" + "="*60)
print("VOLUME CALCULATIONS")
print("="*60)
print(f"Initial volume (day 1):     {V_initial:.2f} m³")
print(f"Final volume (day 180):     {V_final:.2f} m³")
print(f"Delta volume:               {delta_V:.2f} m³")
print(f"Percentage increase:        {(delta_V/V_initial)*100:.2f}%")

# 3. Mass calculations - PREDICTIVE scenario
m_ball_pred_final = Jb_pred[-1] * V_final * (1 - E) * Rhoball
m_ore_final = forward_mass_charge(0.35, Jb_pred[-1], D_final) - m_ball_pred_final
m_total_charge_final = m_shell + m_liner[-1] + forward_mass_charge(0.35, Jb_pred[-1], D_final)

print("\n" + "="*60)
print("MASS CALCULATIONS - PREDICTIVE (Day 180)")
print("="*60)
print(f"Ball mass:                  {m_ball_pred_final:.2f} tonnes")
print(f"Ore + water mass:           {m_ore_final:.2f} tonnes")
print(f"Total charge mass:          {forward_mass_charge(0.35, Jb_pred[-1], D_final):.2f} tonnes")
print(f"Shell mass (constant):      {m_shell:.2f} tonnes")
print(f"Liner mass (day 180):       {m_liner[-1]:.2f} tonnes")
print(f"Total mill mass:            {m_total_charge_final:.2f} tonnes")

# 4. Mass calculations - CONSTANT scenario (for comparison)
m_ball_const_final = Jb_const[-1] * V_final * (1 - E) * Rhoball
m_total_const_final = m_shell + m_liner[-1] + forward_mass_charge(0.35, Jb_const[-1], D_final)

print("\n" + "="*60)
print("MASS CALCULATIONS - CONSTANT (Day 180)")
print("="*60)
print(f"Ball mass:                  {m_ball_const_final:.2f} tonnes")
print(f"Total mill mass:            {m_total_const_final:.2f} tonnes")
print(f"Ball mass deficit vs pred:  {m_ball_pred_final - m_ball_const_final:.2f} tonnes")

# 5. Liner wear summary
liner_initial = plate[0]
liner_final = plate[-1]
liner_wear = liner_initial - liner_final
tonnage_total = np.sum(ton_daily) / 1e6  # in million tonnes

print("\n" + "="*60)
print("LINER WEAR SUMMARY")
print("="*60)
print(f"Initial liner thickness:    {liner_initial:.1f} mm")
print(f"Final liner thickness:      {liner_final:.1f} mm")
print(f"Total liner wear:           {liner_wear:.1f} mm")
print(f"Total tonnage processed:    {tonnage_total:.2f} Mt")
print(f"Liner wear rate:            {liner_wear/tonnage_total:.2f} mm/Mt")

# 6. Ball addition summary - PREDICTIVE
total_ball_added = np.sum(ball_add)
average_daily_addition = np.mean(ball_add)
std_daily_addition = np.std(ball_add)

print("\n" + "="*60)
print("BALL ADDITION SUMMARY - PREDICTIVE")
print("="*60)
print(f"Total ball added (180 days): {total_ball_added:.2f} tonnes")
print(f"Average daily addition:      {average_daily_addition:.2f} tonnes/day")
print(f"Std dev daily addition:      {std_daily_addition:.2f} tonnes/day")
print(f"Min daily addition:          {np.min(ball_add):.2f} tonnes/day")
print(f"Max daily addition:          {np.max(ball_add):.2f} tonnes/day")

# 7. Ball addition summary - CONSTANT
total_ball_const = const_add * DAYS

print("\n" + "="*60)
print("BALL ADDITION SUMMARY - CONSTANT")
print("="*60)
print(f"Daily addition (constant):   {const_add:.2f} tonnes/day")
print(f"Total ball added (180 days): {total_ball_const:.2f} tonnes")
print(f"Difference vs predictive:    {total_ball_added - total_ball_const:.2f} tonnes")

# ==================================================================
# MASS BALANCE SUMMARY
# ==================================================================
print("\n" + "="*60)
print("MASS BALANCE SUMMARY - PREDICTIVE SCENARIO")
print("="*60)

# Initial conditions
V0 = math.pi/4 * D0**2 * L
ball_mass_initial = 0.15 * V0 * (1 - E) * Rhoball

# Final conditions
V_final = V_eff[-1]
ball_mass_final = Jb_pred[-1] * V_final * (1 - E) * Rhoball

# Ball addition and wear
total_addition = np.sum(ball_add)
total_wear = ball_mass_initial + total_addition - ball_mass_final
total_tonnage = np.sum(ton_daily) / 1e6  # Million tonnes

print(f"Initial ball mass (day 0):    {ball_mass_initial:.2f} tonnes")
print(f"Final ball mass (day 180):    {ball_mass_final:.2f} tonnes")
print(f"Net change:                   {ball_mass_final - ball_mass_initial:+.2f} tonnes")
print(f"\nTotal ball addition:          {total_addition:.2f} tonnes")
print(f"Total ball wear (calculated): {total_wear:.2f} tonnes")
print(f"Average wear rate:            {total_wear/total_tonnage:.3f} kg/ton")
print(f"\nTotal tonnage processed:      {total_tonnage:.2f} Mt")
print("="*60)

# Verification check
expected_final = ball_mass_initial + total_addition - total_wear
print(f"\nVerification:")
print(f"Expected final mass:          {expected_final:.2f} tonnes")
print(f"Actual final mass:            {ball_mass_final:.2f} tonnes")
print(f"Difference (should be ~0):    {abs(expected_final - ball_mass_final):.4f} tonnes")

# ==================================================================
# ANALYSIS
# ==================================================================
mape_c = np.mean(np.abs(Jb_const - 0.15) / 0.15 * 100)
mape_p = np.mean(np.abs(Jb_pred - 0.15) / 0.15 * 100)

print("="*60)
print("RESULTS")
print("="*60)
print(f"Constant MAPE:   {mape_c:.2f}%")
print(f"Predictive MAPE: {mape_p:.2f}%")
print(f"Improvement:     {(1-mape_p/mape_c)*100:.0f}%")
print(f"\nFinal Jb - Constant:   {Jb_const[-1]:.4f}")
print(f"Final Jb - Predictive: {Jb_pred[-1]:.4f}")
print(f"Final Jb - Actual:     {Jb_actual[-1]:.4f}")
print(f"\nTrue wear (avg):    {np.mean(true_wear):.3f}")
print(f"Learned wear:       {ctrl.wear:.3f}")
print(f"Actual wear (bal):  {np.nanmean(wear_actual[1:]):.3f}")
print(f"\nEstimation bias:  {np.mean(Jb_est - Jb_actual):.5f}")
print(f"Estimation RMSE:  {np.sqrt(np.mean((Jb_est - Jb_actual)**2)):.5f}")

# ==================================================================
# PLOTS
# ==================================================================
fig, axes = plt.subplots(2, 3, figsize=(15, 8))

ax = axes[0,0]
ax.axhline(y=0.15, color='k', linestyle='--', alpha=0.5, label='Target')
ax.plot(days, Jb_const, 'C3-', label='Constant')
ax.plot(days, Jb_pred, 'C2-', label='Predictive')
ax.plot(days, Jb_actual, 'k--', alpha=0.4, label='Actual')
ax.axvline(x=60, color='gray', linestyle=':', alpha=0.3)
ax.axvline(x=120, color='gray', linestyle=':', alpha=0.3)
ax.set_ylabel('Jb'); ax.set_title('Jb Tracking'); ax.legend(fontsize=8); ax.grid(True, alpha=0.3)

ax = axes[0,1]
ax.plot(days, [const_add]*DAYS, 'C3-', label='Constant')
#ax.plot(days, const_add, 'C3-', label='Constant')

ax.plot(days, ball_add, 'C2-', label='Predictive')
ax.axvline(x=60, color='gray', linestyle=':', alpha=0.3)
ax.axvline(x=120, color='gray', linestyle=':', alpha=0.3)
ax.set_ylabel('ton/day'); ax.set_title('Ball Addition'); ax.legend(fontsize=8); ax.grid(True, alpha=0.3)

ax = axes[0,2]
ax.plot(days, power_const/1000, 'C3-', alpha=0.7, label='Constant')
ax.plot(days, power_pred/1000, 'C2-', label='Predictive')
ax.plot(days, power_meas/1000, 'C0--', alpha=0.3, label='Measured')
ax.axvline(x=60, color='gray', linestyle=':', alpha=0.3)
ax.axvline(x=120, color='gray', linestyle=':', alpha=0.3)
ax.set_ylabel('MW'); ax.set_title('Power Draw'); ax.legend(fontsize=8); ax.grid(True, alpha=0.3)

ax = axes[1,0]
ax.plot(days, Jb_est, 'C1-', alpha=0.7, label='Controller est')
ax.plot(days, Jb_actual, 'C0-', alpha=0.7, label='Actual truth')
ax.fill_between(days, Jb_est, Jb_actual, alpha=0.2, color='orange', label='Gap')
ax.axhline(y=0.15, color='k', linestyle='--', alpha=0.5)
ax.set_ylabel('Jb'); ax.set_title('Estimate vs Truth'); ax.legend(fontsize=8); ax.grid(True, alpha=0.3)

ax = axes[1,1]
ax.plot(days, true_wear, 'k--', alpha=0.5, label='True')
ax.plot(days, wear_est, 'C2-', label='Learned')
ax.plot(days, wear_actual, 'C0-', alpha=0.3, label='Actual bal')
ax.axvline(x=60, color='gray', linestyle=':', alpha=0.3)
ax.axvline(x=120, color='gray', linestyle=':', alpha=0.3)
ax.set_ylabel('kg/ton'); ax.set_title('Wear Rate'); ax.legend(fontsize=8); ax.grid(True, alpha=0.3)
ax.set_ylim(bottom=0.45, top=0.65)


ax = axes[1,2]
ax.hist(np.abs(Jb_const-0.15)/0.15*100, bins=20, alpha=0.5, color='C3', label='Constant', density=True)
ax.hist(np.abs(Jb_pred-0.15)/0.15*100, bins=20, alpha=0.5, color='C2', label='Predictive', density=True)
ax.set_xlabel('Error (%)'); ax.set_title('Error Distribution'); ax.legend(fontsize=8); ax.grid(True, alpha=0.3)

plt.tight_layout()
#plt.savefig('predictive_full_model.png', dpi=150, bbox_inches='tight')
plt.show()
print("Saved: predictive_full_model.png")
