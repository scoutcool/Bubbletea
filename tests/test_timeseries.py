import decimal
import math
import os, sys

from numpy import record
from pandas.core.frame import DataFrame
from streamlit.elements.arrow import Data

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from lib import bubbletea
import pandas as pd
import json

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


# data = {"columns":["amount"],"index":[1628250163000,1628321616000,1628286666000,1628414967000,1628637067000,1628359880000,1628462086000,1628195442000,1628557953000,1628649442000,1628286981000,1628203363000,1628474912000,1628523512000,1628303809000,1628429503000,1628162884000,1628364832000,1628301394000,1628439965000,1628466867000,1628637810000,1628389373000,1628606805000,1628241274000,1628406746000,1628525158000,1628228928000,1628312097000,1628113308000,1628486611000,1628435525000,1628258574000,1628441061000,1628633872000,1628562693000,1628339846000,1628646300000,1628307648000,1628352185000],"data":[[502.0],[80.40244458],[574.4757487141],[115.8754306503],[323.2267],[80.0],[261.0005837339],[307.42155],[89.93207518],[8081.3108643392],[59.55941375],[711.85553],[500.30644619],[1400.5852135196],[247.5483848072],[59.0],[365.0],[148.8],[243.0788],[132.7333],[119.6223925114],[12.1610144017],[135.0],[1400.5852135196],[49.98785361],[37.5],[7184.8985895658],[49.98785361],[2000.0],[248.1050947031],[20.0],[756.0438343424],[2500.0],[1097.4049817962],[1000.0],[5500.0],[711.85553],[5700.8194566415],[50.0],[177.4237207849]]}
# df = pd.DataFrame(data=data['data'], columns=data['columns'], index=data['index'])
# df.index = pd.to_datetime(df.index,unit='ms')
# r = df[['amount']].resample('D')
# f = getattr(r, 'sum')
# df = f()
# print(df)


# data = {"columns":["index","timestamp","amount","round.id"],"index":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41],"data":[[0,1628250163000,502.0,"2251"],[1,1628321616000,80.40244458,"2252"],[2,1628286666000,574.4757487141,"2252"],[3,1628414967000,115.8754306503,"2254"],[4,1628637067000,323.2267,"2257"],[5,1628359880000,80.0,"2253"],[6,1628462086000,261.0005837339,"2254"],[7,1628195442000,307.42155,"2251"],[8,1628557953000,89.93207518,"2255"],[9,1628649442000,8081.3108643392,"2257"],[10,1628286981000,59.55941375,"2252"],[11,1628203363000,711.85553,"2251"],[12,1628474912000,500.30644619,"2254"],[13,1628523512000,1400.5852135196,"2255"],[14,1628303809000,247.5483848072,"2252"],[15,1628429503000,59.0,"2254"],[16,1628162884000,365.0,"2250"],[17,1628364832000,148.8,"2253"],[18,1628301394000,243.0788,"2252"],[19,1628439965000,132.7333,"2254"],[20,1628466867000,119.6223925114,"2254"],[21,1628637810000,12.1610144017,"2257"],[22,1628389373000,135.0,"2253"],[23,1628606805000,1400.5852135196,"2256"],[0,1628241274000,49.98785361,"2251"],[0,1628406746000,37.5,"2253"],[1,1628525158000,7184.8985895658,"2255"],[2,1628228928000,49.98785361,"2251"],[3,1628312097000,2000.0,"2252"],[4,1628486611000,20.0,"2255"],[5,1628435525000,756.0438343424,"2254"],[6,1628258574000,2500.0,"2252"],[7,1628441061000,1097.4049817962,"2254"],[8,1628654595000,160.0,"2257"],[9,1628633872000,1000.0,"2256"],[10,1628562693000,5500.0,"2256"],[11,1628339846000,711.85553,"2253"],[12,1628695916000,23.5835925133,"2257"],[13,1628646300000,5700.8194566415,"2257"],[14,1628307648000,50.0,"2252"],[15,1628352185000,177.4237207849,"2253"],[16,1628695391000,5000.0,"2257"]]}

# df_amount = pd.DataFrame(data=data['data'],index=data['index'], columns=data['columns'])
# df_amount['timestamp'] = pd.to_datetime(df_amount['timestamp'],unit='ms')
# df_amount.set_index('timestamp', inplace=True)

# df_amount_over_time = bubbletea.beta_aggregate_timeseries(
#         df_amount,
#         time_column="timestamp",
#         interval=bubbletea.TimeseriesInterval.DAILY,
#         columns=[
#             bubbletea.ColumnConfig(
#                 name="amount",
#                 type=bubbletea.ColumnType.bigdecimal,
#                 aggregate_method=bubbletea.AggregateMethod.SUM,
#                 na_fill_value=0.0,
#             )
#         ],
#     )
# print(df_amount_over_time)

# # weekly_data_sets = [
# #     {
# #         "data":[
# #             {"time":1607954665, "amount":1, "rate":1.1},    #12/14/2020
# #             {"time":1608229389, "amount":1, "rate":1.1},    #12/17/2020
# #             {"time":1610907789, "amount":2, "rate":1.2},    #01/17/2021
# #         ]
# #     },
# #     {
# #         "data":[
# #             {"time":1608229389, "amount":1, "rate":1.1},    #12/17/2020
# #             {"time":1610907789, "amount":2, "rate":1.2},    #01/17/2021
# #         ]
# #     },
# #     {
# #         "data": []
# #     }
# # ]
# # print('~~~~weekly output~~~')
# # for data_set in weekly_data_sets:
# #     df = bubbletea.beta_aggregate_timeseries(
# #         data = data_set["data"],
# #         time_column='time',
# #         interval=bubbletea.TimeseriesInterval.WEEKLY,
# #         columns=[
# #             bubbletea.ColumnConfig(name='amount', 
# #                     aggregate_method=bubbletea.AggregateMethod.SUM, 
# #                     na_fill_value=0.0,
# #                     type=bubbletea.ColumnType.float),
# #             bubbletea.ColumnConfig(name='rate', 
# #                     aggregate_method=bubbletea.AggregateMethod.LAST, 
# #                     na_fill_method=bubbletea.NaInterpolationMethod.FORDWARD_FILL,
# #                     type=bubbletea.ColumnType.float)
# #         ]
# #     )
# #     print(df)


# # monthly_data_sets = [
# #     {
# #         "data":[
# #             {"time":1607212800, "amount":1, "rate":1.1},    #12/06/2020
# #             {"time":1609459200, "amount":1, "rate":1.1},    #01/01/2020
# #             {"time":1614470400, "amount":2, "rate":1.2},    #02/28/2021
# #         ]
# #     },
# #     {
# #         "data":[
# #             {"time":1608229389, "amount":1, "rate":1.1},    #12/17/2020
# #             {"time":1610907789, "amount":2, "rate":1.2},    #01/17/2021
# #         ]
# #     },
# # ]
# # print('~~~~monthly output~~~')
# # for data_set in monthly_data_sets:
# #     df = bubbletea.beta_aggregate_timeseries(
# #         data = data_set["data"],
# #         time_column='time',
# #         interval=bubbletea.TimeseriesInterval.MONTHLY,
# #         columns=[
# #             bubbletea.ColumnConfig(name='amount', 
# #                     aggregate_method=bubbletea.AggregateMethod.SUM, 
# #                     na_fill_value=0.0,
# #                     type=bubbletea.ColumnType.float),
# #             bubbletea.ColumnConfig(name='rate', 
# #                     aggregate_method=bubbletea.AggregateMethod.LAST, 
# #                     na_fill_method=bubbletea.NaInterpolationMethod.FORDWARD_FILL,
# #                     type=bubbletea.ColumnType.float)
# #         ]
# #     )
# #     print(df)

data ={"columns":["id","timestamp","txEth","txHash","contract.address","contract.name"],"index":[2636,2975,3867,3868,4113,4200,4905,6815,7320,8413,9943,10073,10322,10647,10944,11116,11474,12169,12230,12253,12606,12610,13412,13931,14400,14740,15072,15317,15472,15922,16187,16233,17046,17666,17971,18746,19238,19304,19644,20805,22591,23173,23816,23882,24499,25094,25582,25845,25876,26191,26265,26924,27103,27215,29352,29663,29752,30011,31361],"data":[["0x15c7ab6b8910c5f5d750d1ce4aa278a2e35020414d2f50eba01556468f096a30 415",1633005977.0,0.0,"0x15c7ab6b8910c5f5d750d1ce4aa278a2e35020414d2f50eba01556468f096a30","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0x183321e5b442fbc48a8b3b8a5231348df13a9883170a646b656c0dd22d23c29d 34",1633008578.0,3890000000.0,"0x183321e5b442fbc48a8b3b8a5231348df13a9883170a646b656c0dd22d23c29d","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0x1edc4280abdac1b8bfd1e58a91d1dd263e43a6381e97f705b6e3a2c529fcbadf 146",1632999630.0,0.0,"0x1edc4280abdac1b8bfd1e58a91d1dd263e43a6381e97f705b6e3a2c529fcbadf","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0x1edc4280abdac1b8bfd1e58a91d1dd263e43a6381e97f705b6e3a2c529fcbadf 148",1632999630.0,0.0,"0x1edc4280abdac1b8bfd1e58a91d1dd263e43a6381e97f705b6e3a2c529fcbadf","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0x20ee166c3b06fc13afbc25a8424d0d541fb45bc8bc47d5e3561c1a47c7ab121d 303",1633006092.0,3910000000.0,"0x20ee166c3b06fc13afbc25a8424d0d541fb45bc8bc47d5e3561c1a47c7ab121d","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0x21db5f30394b4671b696d01a996a5978e55121a459ef5ed3b3a60ecfc7dc32e4 257",1633013486.0,3980000000.0,"0x21db5f30394b4671b696d01a996a5978e55121a459ef5ed3b3a60ecfc7dc32e4","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0x2885a32e4f4e20ed62259fc4fc191f035864142da76b71fcab30d24de8d4bd5e 65",1633001170.0,6500000000.0,"0x2885a32e4f4e20ed62259fc4fc191f035864142da76b71fcab30d24de8d4bd5e","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0x38ff3a3f520ade1c61d47e00a936fec67402fc6bae5b1a6d81d1947cf610feca 66",1633020252.0,0.0,"0x38ff3a3f520ade1c61d47e00a936fec67402fc6bae5b1a6d81d1947cf610feca","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0x3c6f8debbdce1de96112fb7a4c867bd2ec59fe67a3a370cc3cdf47e1b78a01d7 38",1633000710.0,4000000000.0,"0x3c6f8debbdce1de96112fb7a4c867bd2ec59fe67a3a370cc3cdf47e1b78a01d7","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0x453bd8787e98c0fd96969cfac7e88647d0aed91883164fe89ef3d341998d8150 459",1633007955.0,3880000000.0,"0x453bd8787e98c0fd96969cfac7e88647d0aed91883164fe89ef3d341998d8150","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0x50ec780b3ecab3189964d05c5fe53b3f889e4c82c42d177705a6009056ea901e 216",1633002381.0,3949000000.0,"0x50ec780b3ecab3189964d05c5fe53b3f889e4c82c42d177705a6009056ea901e","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0x520764d551fb1dd3d555d19ee555f4e8f77b0428a8fead40f6900c98d998efdd 153",1633013903.0,4000000000.0,"0x520764d551fb1dd3d555d19ee555f4e8f77b0428a8fead40f6900c98d998efdd","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0x546d862c30a755184ab05dda818e81ba69b2eb9cbdbd867d706bda889b8499bf 311",1633020171.0,0.0,"0x546d862c30a755184ab05dda818e81ba69b2eb9cbdbd867d706bda889b8499bf","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0x56ebf7a0e3ee314a4351d6a95f2ab4c3f07c7aeece278c10d790b7e11853f022 414",1633013202.0,3900000000.0,"0x56ebf7a0e3ee314a4351d6a95f2ab4c3f07c7aeece278c10d790b7e11853f022","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0x598c41e87e6c5b6f3e793d9f19789dbc26fd34cf824bef4e0d8ec136995001c0 398",1633011521.0,3900000000.0,"0x598c41e87e6c5b6f3e793d9f19789dbc26fd34cf824bef4e0d8ec136995001c0","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0x5ba25ef6e9a69bb0e75cdc04296639db964e7b04d16c68d9d6baf066c3afc414 376",1633000885.0,7500000000.0,"0x5ba25ef6e9a69bb0e75cdc04296639db964e7b04d16c68d9d6baf066c3afc414","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0x5e7afc86379eaa55ecb459b9ab3b72ff3b2db9fe668d1e965023c05bb2968d4a 114",1633019456.0,0.0,"0x5e7afc86379eaa55ecb459b9ab3b72ff3b2db9fe668d1e965023c05bb2968d4a","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0x63f386e5f1bf0fc4a07aa6c9973efc864233b885bfe0ec7edf019aa84d7eaef7 231",1633009879.0,0.0,"0x63f386e5f1bf0fc4a07aa6c9973efc864233b885bfe0ec7edf019aa84d7eaef7","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0x649c80862b22c0de734b5dc33a5ed45d711bc4dd6b4f95ed3fb41edb2cbb6ab5 233",1633007729.0,0.0,"0x649c80862b22c0de734b5dc33a5ed45d711bc4dd6b4f95ed3fb41edb2cbb6ab5","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0x64dadf53d4c7fe56058c4728f6f7ff1ab29fa81bbb514adc8868fb7caaf4a7f2 530",1633020039.0,0.0,"0x64dadf53d4c7fe56058c4728f6f7ff1ab29fa81bbb514adc8868fb7caaf4a7f2","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0x6746017cf39b2a7b3ea55a516bbf64c4b9a13cc78307b1be77a4e3ead0dcfce3 256",1633016856.0,4180000000.0,"0x6746017cf39b2a7b3ea55a516bbf64c4b9a13cc78307b1be77a4e3ead0dcfce3","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0x67650564dfd8e8300b97e1e71e5280f2227801fb71935e3f034146d36ea58e46 381",1633005261.0,3999900000.0,"0x67650564dfd8e8300b97e1e71e5280f2227801fb71935e3f034146d36ea58e46","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0x6dfb80ef627bd2bc06a0869387fd44aebfb0cc8992f85c3e1e7725b940d24374 56",1633002942.0,4000000000.0,"0x6dfb80ef627bd2bc06a0869387fd44aebfb0cc8992f85c3e1e7725b940d24374","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0x719ec72d2e26e1b4b3b0f514f190e5967b772554f7dccb3d7fa557c95b7e38b4 204",1633011934.0,3750000000.0,"0x719ec72d2e26e1b4b3b0f514f190e5967b772554f7dccb3d7fa557c95b7e38b4","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0x74eeece782ffab4a79e537de71b7d5c41d8c3cb9e471cdddf1ef99203ae76e37 222",1633003727.0,3950000000.0,"0x74eeece782ffab4a79e537de71b7d5c41d8c3cb9e471cdddf1ef99203ae76e37","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0x777f3fa912b7d2bcace91769b6d57632b904773c2354b6cd3844241a78a87321 508",1633013379.0,0.0,"0x777f3fa912b7d2bcace91769b6d57632b904773c2354b6cd3844241a78a87321","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0x7a0606d1aa71f033918623a91aa898f5c2c21757facb7bdabc81cf928e3b394f 37",1633014145.0,3800000000.0,"0x7a0606d1aa71f033918623a91aa898f5c2c21757facb7bdabc81cf928e3b394f","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0x7bd5391fd695d38a23534d62e276a7a2ffa261dd98d8a55857e2fc264e4cdcdc 520",1633011612.0,5000000.0,"0x7bd5391fd695d38a23534d62e276a7a2ffa261dd98d8a55857e2fc264e4cdcdc","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0x7d3298a0ab74b2c97cd70b01b0c0a37d94b2206f09980cb036b4d00c3852794f 117",1633020201.0,0.0,"0x7d3298a0ab74b2c97cd70b01b0c0a37d94b2206f09980cb036b4d00c3852794f","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0x81824e71cc7046107b8789d6d7e5b818326e8b92751fda717f9aaec06fa3bafd 393",1633017644.0,3890000000.0,"0x81824e71cc7046107b8789d6d7e5b818326e8b92751fda717f9aaec06fa3bafd","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0x83d10e3b91c1258b57a755310bbfdd9e133c2de8c86a72cc8e37c758e5235f40 52",1633008519.0,3750000000.0,"0x83d10e3b91c1258b57a755310bbfdd9e133c2de8c86a72cc8e37c758e5235f40","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0x8449f53676a7f536f7b9a154a20937857e6c3fbb434311581a8b59fe159cb139 396",1633006148.0,3985000000.0,"0x8449f53676a7f536f7b9a154a20937857e6c3fbb434311581a8b59fe159cb139","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0x8a544d2a02c5271e44240f8f9c356ea6f2b17b981da805eba3bf8606543f2022 141",1633015714.0,4200000000.0,"0x8a544d2a02c5271e44240f8f9c356ea6f2b17b981da805eba3bf8606543f2022","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0x8f2d83a379a0a589f0ec536ce6ff46a3938dbb4701686a14d118bbe4277e7c57 430",1633011779.0,5000000000.0,"0x8f2d83a379a0a589f0ec536ce6ff46a3938dbb4701686a14d118bbe4277e7c57","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0x91bc15c3413a50ec0701c5aeb1675f2e14cb97b060249192be3f113920a046ec 152",1632999747.0,3543000000.0,"0x91bc15c3413a50ec0701c5aeb1675f2e14cb97b060249192be3f113920a046ec","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0x97aade14056ad483f8301e6bfdb8b8b8102e7ae2046d9fbe8d41452c760a2bd0 423",1633007397.0,3988000000.0,"0x97aade14056ad483f8301e6bfdb8b8b8102e7ae2046d9fbe8d41452c760a2bd0","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0x9ba41fb27f2b8c8b289d5c4c3454793f6dde8c379e8db6a01875022f6a098ec1 290",1633007192.0,0.0,"0x9ba41fb27f2b8c8b289d5c4c3454793f6dde8c379e8db6a01875022f6a098ec1","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0x9c14ff407b6dc6e7b2361319f70eae032786eefdd86315b32f03e499ed9de10b 356",1633008735.0,3949000000.0,"0x9c14ff407b6dc6e7b2361319f70eae032786eefdd86315b32f03e499ed9de10b","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0x9ebab0102522ff1cfd4083933653633fdf911a257d76c8403188ae10397a5f42 67",1633004154.0,3990000000.0,"0x9ebab0102522ff1cfd4083933653633fdf911a257d76c8403188ae10397a5f42","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0xa7d08195e0a676044666696abbb3e75664abdd792ae03f863e6fddf134a87056 241",1633020171.0,0.0,"0xa7d08195e0a676044666696abbb3e75664abdd792ae03f863e6fddf134a87056","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0xb431a79f7a4c6ff7177c4bf673454b0b15754e7ae09ac876d6a2f097669d27ea 209",1633001615.0,3948000000.0,"0xb431a79f7a4c6ff7177c4bf673454b0b15754e7ae09ac876d6a2f097669d27ea","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0xb9a6fb5c862fcb7b526883dff804c6903b7f8a1e0d332e863e4ea5cad043fa3e 420",1633019064.0,4200000000.0,"0xb9a6fb5c862fcb7b526883dff804c6903b7f8a1e0d332e863e4ea5cad043fa3e","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0xbe6935f00a0465be020b8d9ed788272bb12e3eec18354306686b0df9d7f4b0e2 385",1633018881.0,3500000000.0,"0xbe6935f00a0465be020b8d9ed788272bb12e3eec18354306686b0df9d7f4b0e2","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0xbef54c65d1cd289afb3d3f0ab6eaaaf066e08539a570e3ed10547769d20a35f5 759",1633007153.0,3800000000.0,"0xbef54c65d1cd289afb3d3f0ab6eaaaf066e08539a570e3ed10547769d20a35f5","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0xc3d3667ab79998931ee9be7768ee6e18522e2da9ac072be49b3405aecb9fe7e8 77",1633001050.0,4900000000.0,"0xc3d3667ab79998931ee9be7768ee6e18522e2da9ac072be49b3405aecb9fe7e8","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0xc8fd5b5379b6e699b72f610f760fa489294ebaa5b6986b7e6b5320dfdc4cf0ce 41",1633004703.0,4000000000.0,"0xc8fd5b5379b6e699b72f610f760fa489294ebaa5b6986b7e6b5320dfdc4cf0ce","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0xcce550619488daaa9fac91e0eb0133130a7c72aeed0affea693458b677568414 131",1633014394.0,3825000000.0,"0xcce550619488daaa9fac91e0eb0133130a7c72aeed0affea693458b677568414","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0xceeb3142bd2c7d369eb578259d995884a861a92eafa08145ba51625ffe4d7a62 103",1633000211.0,4590000000.0,"0xceeb3142bd2c7d369eb578259d995884a861a92eafa08145ba51625ffe4d7a62","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0xcf2cfd5821b16e3250fcddd16700485fb7cab0ec7c1b1e68b9d162d1cc8d01f1 464",1633019064.0,0.0,"0xcf2cfd5821b16e3250fcddd16700485fb7cab0ec7c1b1e68b9d162d1cc8d01f1","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0xd1f7b9f2c66b54ba67170856e5f587ce4298a725fcdffc0081fa6b65c16cead7 397",1633005436.0,5510000000.0,"0xd1f7b9f2c66b54ba67170856e5f587ce4298a725fcdffc0081fa6b65c16cead7","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0xd2b3db179332a78762943a5ea8f287228d955a297c974b8275aadca61bf062e1 183",1633003438.0,3948900000.0,"0xd2b3db179332a78762943a5ea8f287228d955a297c974b8275aadca61bf062e1","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0xd7188b859f6b6dda365a9c5e351c226c9f7d5dbfad636c0c000cd1169a6e8180 296",1633003032.0,0.0,"0xd7188b859f6b6dda365a9c5e351c226c9f7d5dbfad636c0c000cd1169a6e8180","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0xd87cfc4359b75d17661b259a10ba2b9e21e2c0f02cfc2ee835be6ae45490c3ce 314",1633009385.0,3990000000.0,"0xd87cfc4359b75d17661b259a10ba2b9e21e2c0f02cfc2ee835be6ae45490c3ce","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0xd985881d7e887e27de5606625009836eaf15d28bb8e40b4caeec641e9362d6d3 206",1633003438.0,4443200000.0,"0xd985881d7e887e27de5606625009836eaf15d28bb8e40b4caeec641e9362d6d3","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0xeb4f1f53b55d8c0b1fbac9862aa7ea73a5ef69a8ceaf78820ca983ee64ac0b62 47",1633001211.0,4000000000.0,"0xeb4f1f53b55d8c0b1fbac9862aa7ea73a5ef69a8ceaf78820ca983ee64ac0b62","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0xed8631c138d4b235f19da859d8427d335d6f79e33cc153fb388e6be0d0e4c8f3 225",1633013010.0,0.0,"0xed8631c138d4b235f19da859d8427d335d6f79e33cc153fb388e6be0d0e4c8f3","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0xee29b9033f4cf44711df4bdf2d3b91ac67b7eca284befd93a5cca817155cfd40 363",1633010982.0,4000000000.0,"0xee29b9033f4cf44711df4bdf2d3b91ac67b7eca284befd93a5cca817155cfd40","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0xf05290dcccd60d88667e415cd46508020b14e2ea2e892f57d54dae2f821de475 393",1633000036.0,3890000000.0,"0xf05290dcccd60d88667e415cd46508020b14e2ea2e892f57d54dae2f821de475","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"],["0xfbafd59fc1eb9c592590015cdda6f827fb97b23e9d5821632ea41e57e35fb649 209",1633002122.0,0.0,"0xfbafd59fc1eb9c592590015cdda6f827fb97b23e9d5821632ea41e57e35fb649","0xc92ceddfb8dd984a89fb494c376f9a48b999aafc","Creature World"]]}
df = pd.DataFrame(data=data['data'],index=data['index'], columns=data['columns'])


params = dict()
params['txEth'] = pd.NamedAgg('txEth', bubbletea.AggregateMethod.LAST)
params['timestamp'] = pd.NamedAgg('timestamp', bubbletea.AggregateMethod.LAST)
df_summary = df.groupby('txHash').agg(**params)
print(df_summary)

df = bubbletea.beta_aggregate_groupby(
    df,
    by_column="txHash",
    columns=[
        bubbletea.ColumnConfig(
            name="txEth",
            aggregate_method=bubbletea.AggregateMethod.LAST,
            na_fill_value=0.0,
        ),
        bubbletea.ColumnConfig(
            name="timestamp",
            aggregate_method=bubbletea.AggregateMethod.LAST,
            # na_fill_value=0.0,
        )
    ],
)
# df = DataFrame(data)
# df = bubbletea.beta_aggregate_groupby(
#         data=data, 
#         by_column="round.id", 
#         columns=[bubbletea.ColumnConfig(name="amount", aggregate_method=bubbletea.AggregateMethod.SUM, na_fill_value=0.0)]
#     )

print(df)