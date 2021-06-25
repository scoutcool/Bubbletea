import os, sys

from pandas.core.indexes.datetimes import DatetimeIndex
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import lib.earlgrey.transformers.timeseries as ts
import pandas as pd
import json
import math

def is_json(candidate):
    try:
        pd.json_normalize()
        s = str(candidate)
        print(s)
        json.loads(s)
    except ValueError as e:
        print(e)
        return False
    return True

# weekly_data_sets = [
#     {
#         "data":[
#             {"time":1607954665, "amount":1, "rate":1.1},    #12/14/2020
#             {"time":1608229389, "amount":1, "rate":1.1},    #12/17/2020
#             {"time":1610907789, "amount":2, "rate":1.2},    #01/17/2021
#         ]
#     },
#     {
#         "data":[
#             {"time":1608229389, "amount":1, "rate":1.1},    #12/17/2020
#             {"time":1610907789, "amount":2, "rate":1.2},    #01/17/2021
#         ]
#     },
# ]
# print('~~~~weekly output~~~')
# for data_set in weekly_data_sets:
#     df = ts.aggregate_timeseries(
#         data = data_set["data"],
#         time_column='time',
#         interval=ts.TimeseriesInterval.WEEKLY,
#         columns=[
#             ts.ColumnConfig(name='amount', 
#                     aggregate_method=ts.AggregateMethod.SUM, 
#                     na_fill_value=0.0,
#                     type=ts.ColumnType.float),
#             ts.ColumnConfig(name='rate', 
#                     aggregate_method=ts.AggregateMethod.LAST, 
#                     na_fill_method=ts.NaInterpolationMethod.FORDWARD_FILL,
#                     type=ts.ColumnType.float)
#         ]
#     )
#     print(df)


# monthly_data_sets = [
#     {
#         "data":[
#             {"time":1607212800, "amount":1, "rate":1.1},    #12/06/2020
#             {"time":1609459200, "amount":1, "rate":1.1},    #01/01/2020
#             {"time":1614470400, "amount":2, "rate":1.2},    #02/28/2021
#         ]
#     },
#     {
#         "data":[
#             {"time":1608229389, "amount":1, "rate":1.1},    #12/17/2020
#             {"time":1610907789, "amount":2, "rate":1.2},    #01/17/2021
#         ]
#     },
# ]
# print('~~~~monthly output~~~')
# for data_set in monthly_data_sets:
#     df = ts.aggregate_timeseries(
#         data = data_set["data"],
#         time_column='time',
#         interval=ts.TimeseriesInterval.MONTHLY,
#         columns=[
#             ts.ColumnConfig(name='amount', 
#                     aggregate_method=ts.AggregateMethod.SUM, 
#                     na_fill_value=0.0,
#                     type=ts.ColumnType.float),
#             ts.ColumnConfig(name='rate', 
#                     aggregate_method=ts.AggregateMethod.LAST, 
#                     na_fill_method=ts.NaInterpolationMethod.FORDWARD_FILL,
#                     type=ts.ColumnType.float)
#         ]
#     )
#     print(df)

data =[{"index":0,"timestamp":1624491090000,"amount":"5","round.id":"2203"},{"index":1,"timestamp":1624439813000,"amount":"547.629899125388326601","round.id":"2203"},{"index":2,"timestamp":1624051798000,"amount":"73.892474980964350941","round.id":"2198"},{"index":3,"timestamp":1623936195000,"amount":"2.278677313065779378","round.id":"2196"},{"index":4,"timestamp":1624473692000,"amount":"222.903518801217093934","round.id":"2203"},{"index":5,"timestamp":1624139845000,"amount":"96","round.id":"2199"},{"index":6,"timestamp":1624411459000,"amount":"31.476637236551998039","round.id":"2202"},{"index":7,"timestamp":1624250860000,"amount":"10.588744563032380491","round.id":"2200"},{"index":8,"timestamp":1623922719000,"amount":"2.068840371444814249","round.id":"2196"},{"index":9,"timestamp":1624139250000,"amount":"12.943","round.id":"2199"},{"index":10,"timestamp":1624241354000,"amount":"5","round.id":"2200"},{"index":11,"timestamp":1623979488000,"amount":"38.28856709","round.id":"2197"},{"index":12,"timestamp":1624167887000,"amount":"6.4223","round.id":"2199"},{"index":13,"timestamp":1624169447000,"amount":"7.28859318","round.id":"2199"},{"index":14,"timestamp":1624128316000,"amount":"499.170090981991013434","round.id":"2199"},{"index":15,"timestamp":1623970209000,"amount":"7","round.id":"2197"},{"index":16,"timestamp":1623919659000,"amount":"19.129097032087981888","round.id":"2196"},{"index":17,"timestamp":1624216563000,"amount":"109.84937","round.id":"2200"},{"index":18,"timestamp":1624178587000,"amount":"2.178457879126474989","round.id":"2199"},{"index":19,"timestamp":1624070031000,"amount":"3110","round.id":"2198"},{"index":20,"timestamp":1624411206000,"amount":"19","round.id":"2202"},{"index":21,"timestamp":1624455916000,"amount":"577.840099357811297668","round.id":"2203"},{"index":22,"timestamp":1624168380000,"amount":"6.43212","round.id":"2199"},{"index":23,"timestamp":1624124362000,"amount":"2","round.id":"2198"},{"index":24,"timestamp":1624350503000,"amount":"1.481214350904438227","round.id":"2201"},{"index":25,"timestamp":1624085814000,"amount":"23.98743037767755349","round.id":"2198"},{"index":26,"timestamp":1624071379000,"amount":"10000","round.id":"2198"},{"index":27,"timestamp":1623925105000,"amount":"136.39559562741899568","round.id":"2196"},{"index":28,"timestamp":1624059562000,"amount":"179.94275811","round.id":"2198"},{"index":29,"timestamp":1624368266000,"amount":"70000","round.id":"2202"},{"index":30,"timestamp":1624269515000,"amount":"20921.378781459132152573","round.id":"2200"},{"index":31,"timestamp":1624195602000,"amount":"10","round.id":"2199"},{"index":32,"timestamp":1624213631000,"amount":"2398.054050047438010454","round.id":"2200"},{"index":33,"timestamp":1624410268000,"amount":"235.16285108","round.id":"2202"},{"index":34,"timestamp":1623902787000,"amount":"191.79889452330846","round.id":"2196"},{"index":35,"timestamp":1624396376000,"amount":"0.000001","round.id":"2202"},{"index":36,"timestamp":1624116037000,"amount":"7","round.id":"2198"},{"index":37,"timestamp":1624168655000,"amount":"6.44521232","round.id":"2199"},{"index":38,"timestamp":1624322279000,"amount":"1384.34600603","round.id":"2201"},{"index":39,"timestamp":1624124829000,"amount":"96.02710827850672046","round.id":"2198"},{"index":40,"timestamp":1624085037000,"amount":"15.814057532786691633","round.id":"2198"},{"index":41,"timestamp":1624037529000,"amount":"40","round.id":"2197"},{"index":42,"timestamp":1624406782000,"amount":"5","round.id":"2202"},{"index":43,"timestamp":1623984644000,"amount":"2.141658587867691068","round.id":"2197"},{"index":44,"timestamp":1624169153000,"amount":"6.5412321","round.id":"2199"},{"index":45,"timestamp":1624010423000,"amount":"0.000000000000000003","round.id":"2197"},{"index":46,"timestamp":1624154097000,"amount":"6.41711","round.id":"2199"},{"index":47,"timestamp":1624477156000,"amount":"2.261231379157844417","round.id":"2203"},{"index":48,"timestamp":1624282587000,"amount":"2","round.id":"2201"},{"index":49,"timestamp":1624402445000,"amount":"6.55607678","round.id":"2202"},{"index":50,"timestamp":1624473423000,"amount":"2.147822405669437056","round.id":"2203"},{"index":51,"timestamp":1624035314000,"amount":"491.453401328011131172","round.id":"2197"},{"index":52,"timestamp":1624360146000,"amount":"2.09","round.id":"2202"},{"index":53,"timestamp":1624440675000,"amount":"6.07945328488623565","round.id":"2203"},{"index":54,"timestamp":1624047292000,"amount":"66.130861146","round.id":"2198"},{"index":55,"timestamp":1624067738000,"amount":"63.345120134376772478","round.id":"2198"},{"index":56,"timestamp":1624333898000,"amount":"170.796966468360011657","round.id":"2201"},{"index":57,"timestamp":1624168907000,"amount":"6.4495424","round.id":"2199"},{"index":58,"timestamp":1624335573000,"amount":"500.575213882864188985","round.id":"2201"},{"index":59,"timestamp":1624166856000,"amount":"6.421","round.id":"2199"},{"index":60,"timestamp":1624475034000,"amount":"210","round.id":"2203"},{"index":61,"timestamp":1624458013000,"amount":"98.0294800131506297","round.id":"2203"},{"index":62,"timestamp":1624204753000,"amount":"6.525491606226311753","round.id":"2200"},{"index":63,"timestamp":1624423299000,"amount":"497","round.id":"2202"},{"index":64,"timestamp":1624038843000,"amount":"314.5","round.id":"2197"},{"index":65,"timestamp":1624401655000,"amount":"23.583592513336321653","round.id":"2202"},{"index":66,"timestamp":1624056012000,"amount":"499","round.id":"2198"},{"index":67,"timestamp":1624038273000,"amount":"16.11497826","round.id":"2197"},{"index":68,"timestamp":1624157545000,"amount":"9.40632192292178236","round.id":"2199"},{"index":69,"timestamp":1624285310000,"amount":"70.617","round.id":"2201"},{"index":70,"timestamp":1624211602000,"amount":"1647.020796223035386256","round.id":"2200"},{"index":71,"timestamp":1624255613000,"amount":"7.426602972519403328","round.id":"2200"},{"index":72,"timestamp":1624244587000,"amount":"190.55207476962206575","round.id":"2200"},{"index":73,"timestamp":1623937575000,"amount":"71.740585828866384102","round.id":"2196"},{"index":74,"timestamp":1624477525000,"amount":"549.357889057901244419","round.id":"2203"},{"index":75,"timestamp":1624134125000,"amount":"618.45","round.id":"2199"},{"index":76,"timestamp":1623944647000,"amount":"250000","round.id":"2196"},{"index":77,"timestamp":1623906502000,"amount":"807.678007877582125594","round.id":"2196"},{"index":78,"timestamp":1624143785000,"amount":"160.848571840815089305","round.id":"2199"},{"index":0,"timestamp":1624388187000,"amount":"741.720035963896163553","round.id":"2202"},{"index":1,"timestamp":1624477088000,"amount":"549.357889057901244419","round.id":"2203"},{"index":2,"timestamp":1624285196000,"amount":"6.41711","round.id":"2201"},{"index":3,"timestamp":1624212335000,"amount":"576.771272942333559971","round.id":"2200"},{"index":4,"timestamp":1624034987000,"amount":"350","round.id":"2197"},{"index":0,"timestamp":1624153934000,"amount":"300","round.id":"2199"},{"index":1,"timestamp":1624047160000,"amount":"15758.206250328755386853","round.id":"2198"},{"index":2,"timestamp":1624442835000,"amount":"10.808222089518079125","round.id":"2203"},{"index":3,"timestamp":1624160858000,"amount":"19045.898733490799130065","round.id":"2199"},{"index":4,"timestamp":1624232957000,"amount":"0.002304169606949476","round.id":"2200"},{"index":5,"timestamp":1624390045000,"amount":"124.472481187775624965","round.id":"2202"},{"index":6,"timestamp":1624429233000,"amount":"10","round.id":"2202"},{"index":7,"timestamp":1624186408000,"amount":"194.954608548314833775","round.id":"2199"},{"index":8,"timestamp":1624331391000,"amount":"470.371952834685388218","round.id":"2201"},{"index":9,"timestamp":1624134317000,"amount":"100","round.id":"2199"},{"index":10,"timestamp":1623923485000,"amount":"12.193395","round.id":"2196"},{"index":11,"timestamp":1624479175000,"amount":"7.949512611350961685","round.id":"2203"},{"index":12,"timestamp":1624307449000,"amount":"500","round.id":"2201"},{"index":13,"timestamp":1623933430000,"amount":"4488","round.id":"2196"},{"index":14,"timestamp":1624312320000,"amount":"500","round.id":"2201"},{"index":15,"timestamp":1624138772000,"amount":"94.333250092208752685","round.id":"2199"},{"index":16,"timestamp":1624203399000,"amount":"7.28","round.id":"2200"},{"index":17,"timestamp":1624453220000,"amount":"7.014541437601917724","round.id":"2203"},{"index":18,"timestamp":1624424205000,"amount":"321.225157017317453813","round.id":"2202"},{"index":19,"timestamp":1624139069000,"amount":"9","round.id":"2199"},{"index":20,"timestamp":1624160962000,"amount":"82629.875818990545446745","round.id":"2199"},{"index":21,"timestamp":1624388544000,"amount":"175.623707862862600862","round.id":"2202"},{"index":22,"timestamp":1624233166000,"amount":"180","round.id":"2200"},{"index":23,"timestamp":1624344037000,"amount":"87.526977687575775865","round.id":"2201"},{"index":24,"timestamp":1624162866000,"amount":"40.635995793773085156","round.id":"2199"},{"index":25,"timestamp":1624373339000,"amount":"741.720035963896163553","round.id":"2202"},{"index":26,"timestamp":1624232286000,"amount":"6.41711","round.id":"2200"},{"index":27,"timestamp":1624139520000,"amount":"5000","round.id":"2199"},{"index":28,"timestamp":1624489736000,"amount":"26","round.id":"2203"},{"index":29,"timestamp":1624295047000,"amount":"5800","round.id":"2201"},{"index":30,"timestamp":1624452290000,"amount":"96","round.id":"2203"},{"index":31,"timestamp":1624004028000,"amount":"1631.649199363523408776","round.id":"2197"},{"index":32,"timestamp":1624415123000,"amount":"5000","round.id":"2202"},{"index":33,"timestamp":1624142618000,"amount":"44.717537057999554978","round.id":"2199"},{"index":34,"timestamp":1624148061000,"amount":"306.361144330960303245","round.id":"2199"},{"index":35,"timestamp":1624153334000,"amount":"42.410172234908869546","round.id":"2199"},{"index":36,"timestamp":1624175603000,"amount":"11.593454095166739819","round.id":"2199"},{"index":37,"timestamp":1624030773000,"amount":"462946.767403487365196051","round.id":"2197"},{"index":38,"timestamp":1624187461000,"amount":"4.186980988004901876","round.id":"2199"},{"index":39,"timestamp":1624361028000,"amount":"5","round.id":"2202"},{"index":40,"timestamp":1624452042000,"amount":"1350","round.id":"2203"},{"index":41,"timestamp":1624175773000,"amount":"8.029921833917099358","round.id":"2199"},{"index":42,"timestamp":1624475306000,"amount":"549.357889057901244419","round.id":"2203"},{"index":43,"timestamp":1624339501000,"amount":"53","round.id":"2201"},{"index":44,"timestamp":1624384890000,"amount":"500000","round.id":"2202"},{"index":45,"timestamp":1624442191000,"amount":"7","round.id":"2203"},{"index":46,"timestamp":1624039632000,"amount":"1605.101059840086164844","round.id":"2197"},{"index":47,"timestamp":1624409333000,"amount":"232","round.id":"2202"},{"index":48,"timestamp":1624296239000,"amount":"6.611818776620084244","round.id":"2201"},{"index":49,"timestamp":1624271289000,"amount":"2000.217857369121629214","round.id":"2200"},{"index":50,"timestamp":1624215406000,"amount":"120","round.id":"2200"},{"index":51,"timestamp":1624009640000,"amount":"166.873390434037831172","round.id":"2197"}]
df = ts.aggregate_groupby(
        data=data, 
        by_column="round.id", 
        # columns=[ts.ColumnConfig(name="amount", aggregate_method=ts.AggregateMethod.SUM, na_fill_method=ts.NaInterpolationMethod.FORDWARD_FILL)]
        columns=[ts.ColumnConfig(name="amount", aggregate_method=ts.AggregateMethod.SUM, na_fill_value=0.0)]
    )

print(df)