import streamlit as st
import numpy as np
import pandas as pd
import altair as alt


#https://www.ofgem.gov.uk/energy-price-cap
ele_pricecap_day_GBP = 0.6099
gas_pricecap_day_GBP = 0.3166
StandingCharge_ele_yr_GBP = ele_pricecap_day_GBP * 365
StandingCharge_gas_yr_GBP = gas_pricecap_day_GBP * 365
kWh_price_ele_GBP = 0.2450 #including VAT
kWh_price_gas_GBP = 0.0604 #including VAT

#https://eciu.net/insights/2024/are-green-levies-going-up-in-april-2024

PriceCapBill_ele_GBP = 839
PriceCapBill_gas_GBP = 771
PriceCapBill_ele_VATincl_GBP = 881
PriceCapBill_gas_VATincl_GBP = 809

#Renewable Obligation
RO_ele_GBP = 86
RO_gas_GBP = 0
#Feed-in-Tariff
FIT_ele_GBP = 21
FIT_gas_GBP = 0
#Energy Company Obligation
ECO_ele_GBP = 23
ECO_gas_GBP = 34
#Warm Homes Discount
WHD_ele_GBP = 11
WHD_gas_GBP = 11
#AAHEDC (GB Average)
AAHEDC_ele_GBP = 1
AAHEDC_gas_GBP = 0
#Green Gas Levy
GGL_ele_GBP = 0
GGL_gas_GBP = 0.4
#VAT on levies
VAT_ele_GBP = 7
VAT_gas_GBP = 2

yearly_levy_ele_GBP = RO_ele_GBP + FIT_ele_GBP + ECO_ele_GBP + WHD_ele_GBP + AAHEDC_ele_GBP + GGL_ele_GBP
yearly_levy_gas_GBP = RO_gas_GBP + FIT_gas_GBP + ECO_gas_GBP + WHD_gas_GBP + AAHEDC_gas_GBP + GGL_gas_GBP
yearly_levy_dual_GBP = yearly_levy_ele_GBP + yearly_levy_gas_GBP



#Calculate yearly bill without SC
YearlyBill_ele_exclSC_VATincl_GBP = PriceCapBill_ele_VATincl_GBP - StandingCharge_ele_yr_GBP
YearlyBill_gas_exclSC_VATincl_GBP = PriceCapBill_gas_VATincl_GBP - StandingCharge_gas_yr_GBP

#Calculate unit price per kWh used in https://eciu.net/insights/2024/are-green-levies-going-up-in-april-2024
ele_levies_per_kWh = YearlyBill_ele_exclSC_VATincl_GBP/kWh_price_ele_GBP
gas_levies_per_kWh = YearlyBill_gas_exclSC_VATincl_GBP/kWh_price_gas_GBP

#Find levy as unit rate excluding VAT
ele_levy_unit_rate_GBP_kWh = yearly_levy_ele_GBP/ele_levies_per_kWh
gas_levy_unit_rate_GBP_kWh = yearly_levy_gas_GBP/gas_levies_per_kWh
#Find levy as unit rate including VAT
ele_levy_unit_rate_GBP_kWh_VATincl = ele_levy_unit_rate_GBP_kWh + VAT_ele_GBP/ele_levies_per_kWh
gas_levy_unit_rate_GBP_kWh_VATincl = gas_levy_unit_rate_GBP_kWh + VAT_gas_GBP/gas_levies_per_kWh


EST_ele_unit_price_GBP = 0.22360
EST_E7_off_unit_price_GBP = 0.13047
EST_E7_on_unit_price_GBP = 0.26687

EST_gas_unit_price_GBP = 0.05480
EST_ele_standing_charge_GBP_yr = 219.44
EST_gas_standing_charge_GBP_yr = 114.65
EST_Gas_Boiler_Eff = 0.778


TypicalHomeUse_ele = 2700
LowHomeUse_ele = 1800
HighHomeUse_ele = 4100

TypicalHomeUse_gas = 11500
LowHomeUse_gas = 7500
HighHomeUse_gas = 17000

TypicalHeatDemand = TypicalHomeUse_gas*EST_Gas_Boiler_Eff
LowHeatDemand     = LowHomeUse_gas*EST_Gas_Boiler_Eff
HighHeatDemand    = HighHomeUse_gas*EST_Gas_Boiler_Eff

def getBaselineBill(HomeUse_ele,HomeUse_gas,type="gas",perc_offpeak=0.9,SPF=2):
    HeatDemand     = HomeUse_gas*EST_Gas_Boiler_Eff
    if type=="gas":
        return HomeUse_ele*EST_ele_unit_price_GBP + EST_ele_standing_charge_GBP_yr + HomeUse_gas*EST_gas_unit_price_GBP + EST_gas_standing_charge_GBP_yr
    if type=="E7":
        return (HomeUse_ele + (1-perc_offpeak)*HeatDemand)*EST_E7_on_unit_price_GBP + perc_offpeak*HeatDemand*EST_E7_off_unit_price_GBP + EST_ele_standing_charge_GBP_yr
    if type=="heatpump":
        return (HomeUse_ele + HeatDemand/SPF)*EST_ele_unit_price_GBP + EST_ele_standing_charge_GBP_yr
    if type=="heatpump_gascook":
        return (HomeUse_ele + HeatDemand/SPF)*EST_ele_unit_price_GBP + EST_ele_standing_charge_GBP_yr + EST_gas_standing_charge_GBP_yr
    else:
        print("wrong type")

def BaselineHPswitch(HomeUse_ele,HomeUse_gas,SPF,beforetype="gas",gasStandingCharge=False,perc_offpeak=0.9):
    if beforetype=="gas":
        gasboiler = getBaselineBill(HomeUse_ele,HomeUse_gas,type=beforetype)
        if gasStandingCharge==True:
            heatpump = getBaselineBill(HomeUse_ele,HomeUse_gas,type="heatpump_gascook",SPF=SPF)
            return gasboiler - heatpump
        else:
            heatpump = getBaselineBill(HomeUse_ele,HomeUse_gas,type="heatpump",SPF=SPF)
            return gasboiler - heatpump
        
    if beforetype=="E7":
        storageheater = getBaselineBill(HomeUse_ele,HomeUse_gas,type=beforetype,perc_offpeak=perc_offpeak)
        if gasStandingCharge==True:
            heatpump = getBaselineBill(HomeUse_ele,HomeUse_gas,type="heatpump_gascook",SPF=SPF)
            return storageheater - heatpump
        else:
            heatpump = getBaselineBill(HomeUse_ele,HomeUse_gas,type="heatpump",SPF=SPF)
            return storageheater - heatpump
    

BaselineLowBill_gashome     = getBaselineBill(LowHomeUse_ele,LowHomeUse_gas,type="gas")
BaselineTypicalBill_gashome = getBaselineBill(TypicalHomeUse_ele,TypicalHomeUse_gas,type="gas")
BaselineHighBill_gashome    = getBaselineBill(HighHomeUse_ele,HighHomeUse_gas,type="gas")

#E7 no gas SC, X percent of heating is off peak
off_peak_heating = 0.9
BaselineLowBill_E7     = getBaselineBill(LowHomeUse_ele,LowHomeUse_gas,type="E7",perc_offpeak=off_peak_heating)
BaselineTypicalBill_E7 = getBaselineBill(TypicalHomeUse_ele,TypicalHomeUse_gas,type="E7",perc_offpeak=off_peak_heating)
BaselineHighBill_E7    = getBaselineBill(HighHomeUse_ele,HighHomeUse_gas,type="E7",perc_offpeak=off_peak_heating)


NoLevy_ele_unit_price = EST_ele_unit_price_GBP-ele_levy_unit_rate_GBP_kWh_VATincl
NoLevy_gas_unit_price = EST_gas_unit_price_GBP-gas_levy_unit_rate_GBP_kWh_VATincl

NoLevy_E7_peak_price = EST_E7_on_unit_price_GBP - ele_levy_unit_rate_GBP_kWh_VATincl
NoLevy_E7_off_price = EST_E7_off_unit_price_GBP - ele_levy_unit_rate_GBP_kWh_VATincl

def getNoLevyBill(HomeUse_ele,HomeUse_gas,type="gas",perc_offpeak=0.9,SPF=2):
    HeatDemand     = HomeUse_gas*EST_Gas_Boiler_Eff
    if type=="gas":
        return HomeUse_ele*NoLevy_ele_unit_price + EST_ele_standing_charge_GBP_yr + HomeUse_gas*NoLevy_gas_unit_price + EST_gas_standing_charge_GBP_yr - 1.05*GGL_gas_GBP #1.05 to add VAT onto the GGL
    if type=="E7":
        return (HomeUse_ele + (1-perc_offpeak)*HeatDemand)*NoLevy_E7_peak_price + perc_offpeak*HeatDemand*NoLevy_E7_off_price + EST_ele_standing_charge_GBP_yr
    if type=="heatpump":
        return (HomeUse_ele + HeatDemand/SPF)*NoLevy_ele_unit_price + EST_ele_standing_charge_GBP_yr
    if type=="heatpump_gascook":
        return (HomeUse_ele + HeatDemand/SPF)*NoLevy_ele_unit_price + EST_ele_standing_charge_GBP_yr + EST_gas_standing_charge_GBP_yr - 1.05*GGL_gas_GBP #1.05 to add VAT onto the GGL
    else:
        print("wrong type")

def scenario1saving(HomeUse_ele,HomeUse_gas,type="gas",perc_offpeak=0.9,SPF=2):
    saving = getBaselineBill(HomeUse_ele,HomeUse_gas,type=type,perc_offpeak=perc_offpeak,SPF=SPF) - getNoLevyBill(HomeUse_ele,HomeUse_gas,type=type,perc_offpeak=perc_offpeak,SPF=SPF)
    return saving
def scenario1HPswitch(HomeUse_ele,HomeUse_gas,SPF,beforetype="gas",gasStandingCharge=False,perc_offpeak=0.9):
    if beforetype=="gas":
        gasboiler = getNoLevyBill(HomeUse_ele,HomeUse_gas,type=beforetype)
        if gasStandingCharge==True:
            heatpump = getNoLevyBill(HomeUse_ele,HomeUse_gas,type="heatpump_gascook",SPF=SPF)
            return gasboiler - heatpump
        else:
            heatpump = getNoLevyBill(HomeUse_ele,HomeUse_gas,type="heatpump",SPF=SPF)
            return gasboiler - heatpump
        
    if beforetype=="E7":
        storageheater = getNoLevyBill(HomeUse_ele,HomeUse_gas,type=beforetype,perc_offpeak=perc_offpeak)
        if gasStandingCharge==True:
            heatpump = getNoLevyBill(HomeUse_ele,HomeUse_gas,type="heatpump_gascook",SPF=SPF)
            return storageheater - heatpump
        else:
            heatpump = getNoLevyBill(HomeUse_ele,HomeUse_gas,type="heatpump",SPF=SPF)
            return storageheater - heatpump
    
NoVAT_ele_unit_price = EST_ele_unit_price_GBP/1.05 #remove VAT
NoVAT_gas_unit_price = EST_gas_unit_price_GBP

NoVAT_E7_peak_price = EST_E7_on_unit_price_GBP/1.05 #remove VAT
NoVAT_E7_off_price = EST_E7_off_unit_price_GBP/1.05 #remove VAT

def getNoVATBill(HomeUse_ele,HomeUse_gas,type="gas",perc_offpeak=0.9,SPF=2):
    HeatDemand     = HomeUse_gas*EST_Gas_Boiler_Eff
    if type=="gas":
        return HomeUse_ele*NoVAT_ele_unit_price + EST_ele_standing_charge_GBP_yr + HomeUse_gas*NoVAT_gas_unit_price + EST_gas_standing_charge_GBP_yr
    if type=="E7":
        return (HomeUse_ele + (1-perc_offpeak)*HeatDemand)*NoVAT_E7_peak_price + perc_offpeak*HeatDemand*NoVAT_E7_off_price + EST_ele_standing_charge_GBP_yr
    if type=="heatpump":
        return (HomeUse_ele + HeatDemand/SPF)*NoVAT_ele_unit_price + EST_ele_standing_charge_GBP_yr
    if type=="heatpump_gascook":
        return (HomeUse_ele + HeatDemand/SPF)*NoVAT_ele_unit_price + EST_ele_standing_charge_GBP_yr + EST_gas_standing_charge_GBP_yr
    else:
        print("wrong type")

def scenario2saving(HomeUse_ele,HomeUse_gas,type="gas",perc_offpeak=0.9,SPF=2):
    saving = getBaselineBill(HomeUse_ele,HomeUse_gas,type=type,perc_offpeak=perc_offpeak,SPF=SPF) - getNoVATBill(HomeUse_ele,HomeUse_gas,type=type,perc_offpeak=perc_offpeak,SPF=SPF)
    return saving
def scenario2HPswitch(HomeUse_ele,HomeUse_gas,SPF,beforetype="gas",gasStandingCharge=False,perc_offpeak=0.9):
    if beforetype=="gas":
        gasboiler = getNoVATBill(HomeUse_ele,HomeUse_gas,type=beforetype)
        if gasStandingCharge==True:
            heatpump = getNoVATBill(HomeUse_ele,HomeUse_gas,type="heatpump_gascook",SPF=SPF)
            return gasboiler - heatpump
        else:
            heatpump = getNoVATBill(HomeUse_ele,HomeUse_gas,type="heatpump",SPF=SPF)
            return gasboiler - heatpump
        
    if beforetype=="E7":
        storageheater = getNoVATBill(HomeUse_ele,HomeUse_gas,type=beforetype,perc_offpeak=perc_offpeak)
        if gasStandingCharge==True:
            heatpump = getNoVATBill(HomeUse_ele,HomeUse_gas,type="heatpump_gascook",SPF=SPF)
            return storageheater - heatpump
        else:
            heatpump = getNoVATBill(HomeUse_ele,HomeUse_gas,type="heatpump",SPF=SPF)
            return storageheater - heatpump

def getCleanHeatBill(HomeUse_ele,HomeUse_gas,type="gas",perc_offpeak=0.9,SPF=2,electricity_discount_kWh = 3500):
    HeatDemand     = HomeUse_gas*EST_Gas_Boiler_Eff
    if type=="gas":
        return HomeUse_ele*EST_ele_unit_price_GBP + EST_ele_standing_charge_GBP_yr + HomeUse_gas*EST_gas_unit_price_GBP + EST_gas_standing_charge_GBP_yr
    if type=="E7":
        return (HomeUse_ele + (1-perc_offpeak)*HeatDemand)*EST_E7_on_unit_price_GBP + perc_offpeak*HeatDemand*EST_E7_off_unit_price_GBP + EST_ele_standing_charge_GBP_yr - electricity_discount_kWh*ele_levy_unit_rate_GBP_kWh_VATincl
    if type=="heatpump":
        return (HomeUse_ele + HeatDemand/SPF)*EST_ele_unit_price_GBP + EST_ele_standing_charge_GBP_yr- electricity_discount_kWh*ele_levy_unit_rate_GBP_kWh_VATincl
    if type=="heatpump_gascook":
        return (HomeUse_ele + HeatDemand/SPF)*EST_ele_unit_price_GBP + EST_ele_standing_charge_GBP_yr + EST_gas_standing_charge_GBP_yr- electricity_discount_kWh*ele_levy_unit_rate_GBP_kWh_VATincl
    else:
        print("wrong type")

def scenario3saving(HomeUse_ele,HomeUse_gas,type="gas",perc_offpeak=0.9,SPF=2,electricity_discount_kWh = 3500):
    saving = getBaselineBill(HomeUse_ele,HomeUse_gas,type=type,perc_offpeak=perc_offpeak,SPF=SPF) - getCleanHeatBill(HomeUse_ele,HomeUse_gas,type=type,perc_offpeak=perc_offpeak,SPF=SPF,electricity_discount_kWh=electricity_discount_kWh)
    return saving
def scenario3HPswitch(HomeUse_ele,HomeUse_gas,SPF,beforetype="gas",gasStandingCharge=False,perc_offpeak=0.9,electricity_discount_kWh=3500):
    if beforetype=="gas":
        gasboiler = getCleanHeatBill(HomeUse_ele,HomeUse_gas,type=beforetype,electricity_discount_kWh=electricity_discount_kWh)
        if gasStandingCharge==True:
            heatpump = getCleanHeatBill(HomeUse_ele,HomeUse_gas,type="heatpump_gascook",SPF=SPF,electricity_discount_kWh=electricity_discount_kWh)
            return gasboiler - heatpump
        else:
            heatpump = getCleanHeatBill(HomeUse_ele,HomeUse_gas,type="heatpump",SPF=SPF,electricity_discount_kWh=electricity_discount_kWh)
            return gasboiler - heatpump
        
    if beforetype=="E7":
        storageheater = getCleanHeatBill(HomeUse_ele,HomeUse_gas,type=beforetype,perc_offpeak=perc_offpeak,electricity_discount_kWh=electricity_discount_kWh)
        if gasStandingCharge==True:
            heatpump = getCleanHeatBill(HomeUse_ele,HomeUse_gas,type="heatpump_gascook",SPF=SPF,electricity_discount_kWh=electricity_discount_kWh)
            return storageheater - heatpump
        else:
            heatpump = getCleanHeatBill(HomeUse_ele,HomeUse_gas,type="heatpump",SPF=SPF,electricity_discount_kWh=electricity_discount_kWh)
            return storageheater - heatpump

# Generate the Seasonal Performance Factor (SPF) data
SPF = np.linspace(1, 4, 100)
st.set_page_config(layout="wide")
# Sidebar: Heating type selection
st.sidebar.header("Heating Options Before Switching to Heat Pump")
Before_Heating = st.sidebar.selectbox("Select the current heating type:", ("gas", "E7"))

energyuse = st.sidebar.selectbox("How high is the energy use?",("Low","Typical","High"))
if energyuse=="Low":
    HomeUse_ele = LowHomeUse_ele
    HomeUse_gas = LowHomeUse_gas
if energyuse=="High":
    HomeUse_ele = HighHomeUse_ele
    HomeUse_gas = HighHomeUse_gas
if energyuse=="Typical":
    HomeUse_ele = TypicalHomeUse_ele
    HomeUse_gas = TypicalHomeUse_gas
# Sidebar: Off-peak percentage input
if Before_Heating == "E7":
    OffPeak_percentage = st.sidebar.number_input("Percentage of heating energy used during off-peak:", value=90) / 100
else:
    OffPeak_percentage = 0.9
Scenario = st.sidebar.selectbox("Which scenario?:", ("1. Move all levies completely off bills and onto general taxation",
                                                     "2. Remove VAT from electricity bills only and don't touch levy costs",
                                                     "3. Introduce a clean heat discount"))

if Scenario == "3. Introduce a clean heat discount":
    CleanHeatDiscount = st.sidebar.number_input("What is the assumed heating load of electric homes?", value=3500)
else:
    CleanHeatDiscount = 35000000

# Sidebar: Gas standing charge option
KeepStandingCharge = st.sidebar.checkbox("Keep the gas standing charge (for cooking)?", value=False)

# Calculate Scenario 1 and Baseline data
scenario1 = scenario1HPswitch(HomeUse_ele,
                              HomeUse_gas,
                              beforetype=Before_Heating,
                              gasStandingCharge=KeepStandingCharge,
                              perc_offpeak=OffPeak_percentage,
                              SPF=SPF)

scenario2 = scenario2HPswitch(HomeUse_ele,
                              HomeUse_gas,
                              beforetype=Before_Heating,
                              gasStandingCharge=KeepStandingCharge,
                              perc_offpeak=OffPeak_percentage,
                              SPF=SPF)
scenario3 = scenario3HPswitch(HomeUse_ele,
                              HomeUse_gas,
                              beforetype=Before_Heating,
                              gasStandingCharge=KeepStandingCharge,
                              perc_offpeak=OffPeak_percentage,
                              SPF=SPF,
                              electricity_discount_kWh=CleanHeatDiscount)

baseline = BaselineHPswitch(HomeUse_ele,
                            HomeUse_gas,
                            SPF=SPF,
                            beforetype=Before_Heating,
                            gasStandingCharge=KeepStandingCharge,
                            perc_offpeak=OffPeak_percentage)




# Combine data into a DataFrame for plotting
data = pd.DataFrame({
    'SPF': SPF,
    'Green Levies Removed': scenario1,
    'Now': baseline
})

# Main content
st.title("Heat Pump Savings Comparison")
if Before_Heating == "E7":
    st.write("This chart shows the potential yearly savings from switching to a heat pump from **storage heaters** with and without the levies removed.")
if Before_Heating == "gas":
    st.write("This chart shows the potential yearly savings from switching to a heat pump from a **gas boiler** with and without the levies removed.")

# Find points where the lines meet the Y-axis at 0
scenario1_zero = np.round(np.interp(0, scenario1, SPF),2)
baseline_zero = np.round(np.interp(0, baseline, SPF),2)

# Prepare data for zero crossing points
zero_points = pd.DataFrame({
    'Break-Even SPF': [scenario1_zero, baseline_zero],
    'Savings': [0, 0],
    'Scenario': ['Green Levies Removed', 'Now']
})

# Create an Altair line chart
chart = alt.Chart(data.melt('SPF', var_name='Scenario', value_name='Savings')).mark_line().encode(
    x=alt.X('SPF', title='Seasonal Performance Factor (SPF)'),
    y=alt.Y('Savings', title='Yearly Savings (£)'),
    color='Scenario:N'
).properties(
    width='container',
    height=500
)

# Add points where lines cross the y-axis at 0
points = alt.Chart(zero_points).mark_point(size=100, filled=True).encode(
    x='Break-Even SPF',
    y='Savings',
    color='Scenario:N'
)

# Combine the line chart and points
final_chart = chart + points

# Display the chart in Streamlit
st.altair_chart(final_chart, use_container_width=True)

# Additional explanations
st.write("**SPF** stands for Seasonal Performance Factor, representing the efficiency of the heat pump. "
         "A higher SPF indicates a more efficient heat pump. The Y-axis shows the savings in energy costs "
         "compared to the selected heating type before switching to a heat pump.")