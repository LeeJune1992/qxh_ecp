/**
 * Created with PyCharm.
 * User: seandong
 * Date: 13-2-22
 * Time: 下午4:09
 * To change this template use File | Settings | File Templates.
 */

M1="请选择";
M2="请选择";
M3="请选择";
ShowT=1;		//提示文字 0:不显示 1:显示

//MMMD="心力健快乐老人报（山东）$#心力健全国$快乐老人报|老年日报|中国老年报|文萃报|文摘周刊|家庭医生|#心力健扬子晚报$#心力健新安晚报$#心力健燕赵晚报$#心力健青岛早报$#心力健长沙晚报$#心力健扬州晚报$#心力健福建老年报$#心力健厦门晚报$#心力健楚天都市报$#心力健北京晨报$#心力健老年生活报$#心力健江南保健报$"//john20140218
MMMD="心力健快乐老人报（山东）$#心力健全国$安徽商报6月11日|快乐老人报|老年日报|中国老年报|文萃报|文摘周刊|老年文摘5月8日|老年生活报5月7日|燕赵老年报6月4日|快乐老人报（产品版）|家庭医生|家庭保健6月5日|烟台晚报6月17日|读友报5月16日|晚霞报5月15日|中国老年报5月20日|健康之友5月22日|医药养生5月26日|晚晴报5月28日|山东商报6月12日|北京晨报6月19|威海晚报6月19|每日新报7月2日|老年生活报7月7日|大河文摘7月8日|文萃报7月11日|家庭医生报7月14日|文摘周刊7月46日|北京晨报7月15|半岛都市报7月16|中国老年报7月18|生活文摘7月22日|中国电视7月24日|长沙晚报7月28日|老年文汇报7月29日|江南保健报7月31日|#心力健扬子晚报$#心力健新安晚报$#心力健燕赵晚报$#心力健青岛早报$#心力健长沙晚报$#心力健扬州晚报$#心力健福建老年报$#心力健厦门晚报$#心力健楚天都市报$#心力健北京晨报$#心力健老年生活报$#心力健江南保健报$#心力健济南时报6.18$";
if(ShowT)MMMD=M1+"$"+M2+","+M3+"#"+MMMD;MMMArea=[];MMMP=[];MMMC=[];MMMA=[];MMMN=MMMD.split("#");for(i=0;i<MMMN.length;i++){MMMA[i]=[];TArea=MMMN[i].split("$")[1].split("|");for(j=0;j<TArea.length;j++){MMMA[i][j]=TArea[j].split(",");if(MMMA[i][j].length==1)MMMA[i][j][1]=M3;TArea[j]=TArea[j].split(",")[0]}MMMArea[i]=MMMN[i].split("$")[0]+","+TArea.join(",");MMMP[i]=MMMArea[i].split(",")[0];MMMC[i]=MMMArea[i].split(',')}function MMMS(){this.SelP=document.getElementsByName(arguments[0])[0];this.SelC=document.getElementsByName(arguments[1])[0];this.SelA=document.getElementsByName(arguments[2])[0];this.DefP=this.SelA?arguments[3]:arguments[2];this.DefC=this.SelA?arguments[4]:arguments[3];this.DefA=this.SelA?arguments[5]:arguments[4];this.SelP.MMM=this;this.SelC.MMM=this;this.SelP.onchange=function(){MMMS.SetC(this.MMM)};if(this.SelA)this.SelC.onchange=function(){MMMS.SetA(this.MMM)};MMMS.SetP(this)};MMMS.SetP=function(MMM){for(i=0;i<MMMP.length;i++){MMMPT=MMMPV=MMMP[i];if(MMMPT==M1)MMMPV="";MMM.SelP.options.add(new Option(MMMPT,MMMPV));if(MMM.DefP==MMMPV)MMM.SelP[i].selected=true}MMMS.SetC(MMM)};MMMS.SetC=function(MMM){PI=MMM.SelP.selectedIndex;MMM.SelC.length=0;for(i=1;i<MMMC[PI].length;i++){MMMCT=MMMCV=MMMC[PI][i];if(MMMCT==M2)MMMCV="";MMM.SelC.options.add(new Option(MMMCT,MMMCV));if(MMM.DefC==MMMCV)MMM.SelC[i-1].selected=true}if(MMM.SelA)MMMS.SetA(MMM)};MMMS.SetA=function(MMM){PI=MMM.SelP.selectedIndex;CI=MMM.SelC.selectedIndex;MMM.SelA.length=0;for(i=1;i<MMMA[PI][CI].length;i++){MMMAT=MMMAV=MMMA[PI][CI][i];if(MMMAT==M3)MMMAV="";MMM.SelA.options.add(new Option(MMMAT,MMMAV));if(MMM.DefA==MMMAV)MMM.SelA[i-1].selected=true}}
