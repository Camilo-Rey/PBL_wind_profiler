%% Analyze annual inputs 2019 

clear all
%% Sherman Barn

load('D:\FluxData\Sherman_Barn\SB_2019365_L3.mat');

plottime=datetime(datevec(data.Mdate));
CH4=data.wm;
CO2=data.wc;


CO2_gf=data.wc_gf;
CH4_gf=data.wm_gf;

%% Figure 1
figure;subplot(2,1,1)
plot(plottime,CO2_gf);hold on
plot(plottime,CO2);
yline(0,'--');ylim([-25,25])
legend('ANN Gap filled','Original','Location','Best')
title('CO_2 flux')
ylabel('CO_2 flux (umol m^{-2} s^{-1})')


subplot(2,1,2)
plot(plottime,CH4_gf);hold on
plot(plottime,CH4);
yline(0,'--');ylim([-200,1200])
legend('ANN Gap filled','Original','Location','Best')
title('CH_4 flux')
ylabel('CH_4 flux (nmol m^{-2} s^{-1})')

%% Figure 2

figure;
subplot(2,1,1)
plot(plottime,data.gpp_ANNnight)
yline(0,'--');ylim([-70,8])
legend('ANN Gap filled','Original','Location','Best')
title('GPP')
ylabel('GPP (umol m^{-2} s^{-1})')

subplot(2,1,2)
plot(plottime,data.er_Reichstein)
yline(0,'--');ylim([0,17])
title('Respiration')
ylabel('Resp. (umol m^{-2} s^{-1})')

%%

figure;
plot(plottime,data.er_Reichstein,'-r')
yline(0,'--');ylim([0,35])
title('Respiration')
ylabel('Resp. (umol m^{-2} s^{-1})')

figure;
plot(plottime,data.LE_gf);hold on
ylim([-200,600])
ylabel('H (W m^{-2})')

plot(plottime,data.H_gf)
ylim([-200,600])
ylabel('W m^{-2}')
yline(0,'--');
legend('LE','H','zero')
title('Sensible and Latent Heat')


%% Reflectance
daytime=data.ze<90;

ix=data.DOY<365 & data.DOY >1 & daytime==1 & data.year==2019;

NDVI=Metdata.NDVIraw(ix);
N810=Metdata.NDVI_810out(ix);
gpp=data.gpp_ANNnight(ix);

pltY1=gpp;

figure
subplot(2,1,1)
pltX=N810;
plot(N810,gpp,'.');
title('NIR out')
xlabel('NIR out (810 nm)')
ylabel('GPP (umol m^{-2} s^{-1})')
[a,~,~,~,e]=regress(pltY1,[ones(length(pltX),1),pltX]);lsline
text(0.1,-30,['r^2=' num2str(round(e(1),2)) ',p=' num2str(round(e(3),1))])
text(0.1,-35,['{\ity= }' num2str(round(a(2),1)) '{\itx }+' num2str(round(a(1),2)) ])


subplot(2,1,2)
pltX=N810.*NDVI;
plot(N810.*NDVI,gpp,'.');
title('NDVI *NIR out')
[a,~,~,~,e]=regress(pltY1,[ones(length(pltX),1),pltX]);lsline
text(0.05,-30,['r^2=' num2str(round(e(1),2)) ',p=' num2str(round(e(3),1))])
text(0.05,-35,['{\ity= }' num2str(round(a(2),1)) '{\itx }+' num2str(round(a(1),2)) ])
xlabel('NDVI*NIR out')
ylabel('GPP (umol m^{-2} s^{-1})')

%% Explaining CH4 emissions 

% wind direction
figure
plot(plottime,CH4)
yline(0,'--');ylim([-100,1000])
title('CH_4 flux')
ylabel('Resp. (nmol m^{-2} s^{-1})')
yyaxis right
plot(plottime,data.WD)
ylabel('Wind direction')

% Motion detector
figure
plot(Metdata.Mot,CH4,'.')
yline(0,'--');ylim([-100,1000])
title('Motion Detector vs CH_4 flux')
ylabel('CH4 flux (nmol m^{-2} s^{-1})')
xlabel('Motion counts')

% wind direction cosine
WD=data.WD;
figure
scatter(WD,CH4,[],Metdata.Tsoil_2,'.')
c = colorbar;
c.Label.String = 'Soil temp';
yline(0,'--');ylim([-100,1000])
title('Wind direction vs CH_4 flux')
ylabel('CH4 flux (nmol m^{-2} s^{-1})')
xlabel('Wind direction')

% Soil temp
ST=Metdata.Tsoil_2;%*pi/180);
figure
scatter(ST,CH4,[],data.WD,'.')
c = colorbar;
c.Label.String = 'Win direction';
yline(0,'--');ylim([-100,1000])
title('Soil temp vs CH_4 flux')
ylabel('CH4 flux (nmol m^{-2} s^{-1})')
xlabel('Soil temp (°C)')

% Motion sensor

Mot=Metdata.Mot;%*pi/180);
figure
plot(Mot(WD>260 & WD<360),CH4(WD>260 & WD<360),'.')
c = colorbar;
c.Label.String = 'Win direction';
yline(0,'--');ylim([-100,1000])
title('Soil temp vs CH_4 flux')
ylabel('CH4 flux (nmol m^{-2} s^{-1})')
xlabel('Soil temp (°C)')

% Manual



%% Budgets

CO2_g=[];
CH4_g=[];
CH4_g_SWP=[];
CO2_g_SWP=[];

for i=1:2
start=datenum(2017+i,01,1,0,0,0);
last=datenum(2018+i,01,1,0,0,0);
ix=data.Mdate>=start & data.Mdate<last;

CH4a=CH4_gf(ix);
CO2a=CO2_gf(ix);

CH4_sum=nansum(CH4a)*1800;% nmol m2 Year
CO2_sum=nansum(CO2a)*1800;% umol m2 Year

CO2_g(i)=CO2_sum*12/(10^6);%& g-C m-2 year
CH4_g(i)=CH4_sum*12/(10^9);%& g-C m-2 year

CH4_g_SWP(i)=CH4_g(i)*16/12*45;%& g-CO2 m-2 year
CO2_g_SWP(i)=CO2_g(i)*44/12*1;%& g-CO2 m-2 year

end

CO2_eq=CH4_g_SWP+CO2_g_SWP;

lab=categorical({'2018','2019'});

figure;
subplot(3,1,1)
bar(lab,CO2_g);ylabel('Carbon flux (g-C m^{-2} y^{-1})');
title('CO_2 flux')
subplot(3,1,2)
bar(lab,CH4_g);ylabel('CH4 flux (g-C m^{-2} y^{-1})');
title('CH_4 flux')
subplot(3,1,3)
bar(lab,CO2_eq);ylabel('CO2 eq  (g-CO_2 m^{-2} y^{-1})');
title('Global Warming Potential')

