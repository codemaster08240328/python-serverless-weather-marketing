import json
import boto3

d = {'universe':{}, 'ml':{}}

d['universe']['transactional'] = {
   "label":"Transactions",
   "type":"!group",
   "subfields":{
      "Channel":{
         "type":"select",
         "listValues":[{"value": 'Retail', "title": "FP Store"}
         ,{"value": 'Direct', "title": "Direct"}
         ,{"value": 'Outlet', "title": "Outlet"}],
         "valueSources":[
            "value"
         ]
      },
      "Time Period":{
      "label": 'Time Period (Absolute)',
         "type":"date",
         "fieldSettings":{
            "dateFormat":"MM-DD-YYYY"
         },
         "valueSources":[
            "value"
         ],
           "widgets": {
               "date": {
                       "operators": ['between'],
                       "widgetProps": {
                           "hideOperator": True,
                           "operatorInlineLabel": "between",
                           }
                       },
                   }
      },
        "Days Ahead":{
              "label": 'Days Prior (Relative)',
              "type": 'number',
              "valueSources": ['value', 'field'],
              "fieldSettings": {
                  "min": -2000,
                  "max": 0,
                  "step": 30,
                  "marks": {
                      0: "0",
                      365: "365"
                  }
              },
              "widgets": {
                  "number": {
                          "operators": ['between'],
                          "widgetProps": {
                              "hideOperator": True,
                              "operatorInlineLabel": "between",
                              }
                          },
                      }
          },
      "Transactions":{
         "type":"number",
         "valueSources":[
            "value"
         ]
      },
        "Demand":{
           "type":"number",
           "valueSources":[
              "value"
           ]
        },
      "Units":{
         "type":"number",
         "valueSources":[
            "value"
         ]
      },
    "product_id":{
        "label":"Product ID",
       "type":"multiselect",
                      "widgets": {
                        "multiselect": {
                                    "operators": ['select_any_in']
                        }},
       "listValues":[
       {'value':'29-667', 'title': '29-667'},
{'value':'34-175', 'title': '34-175'},
{'value':'29-668', 'title': '29-668'},
{'value':'34-156', 'title': '34-156'},
{'value':'34-417', 'title': '34-417'},
{'value':'34-158', 'title': '34-158'},
{'value':'34-159', 'title': '34-159'},
{'value':'34-161', 'title': '34-161'},
{'value':'34-385', 'title': '34-385'},
{'value':'34-8542', 'title': '34-8542'},
{'value':'34-8063', 'title': '34-8063'},
{'value':'34-408', 'title': '34-408'},
{'value':'34-405', 'title': '34-405'},
{'value':'34-160', 'title': '34-160'},
{'value':'34-8129', 'title': '34-8129'},
{'value':'34-163', 'title': '34-163'},
{'value':'34-489', 'title': '34-489'},
{'value':'40-606', 'title': '40-606'},
{'value':'34-8130', 'title': '34-8130'},
{'value':'34-8064', 'title': '34-8064'},
{'value':'34-8543', 'title': '34-8543'},
{'value':'34-542', 'title': '34-542'},
{'value':'34-502', 'title': '34-502'},
{'value':'34-476', 'title': '34-476'},
{'value':'34-545', 'title': '34-545'},
{'value':'34-8550', 'title': '34-8550'},
{'value':'34-8136', 'title': '34-8136'},
{'value':'8-784', 'title': '8-784'},
{'value':'8-418', 'title': '8-418'},
{'value':'8-729', 'title': '8-729'},
{'value':'8-772', 'title': '8-772'},
{'value':'31-1984', 'title': '31-1984'},
{'value':'8-805', 'title': '8-805'},
{'value':'8-792', 'title': '8-792'},
{'value':'8-750', 'title': '8-750'},
{'value':'8-850', 'title': '8-850'},
{'value':'8-728', 'title': '8-728'},
{'value':'8-791', 'title': '8-791'},
{'value':'8-960', 'title': '8-960'},
{'value':'8-778', 'title': '8-778'},
{'value':'8-782', 'title': '8-782'},
{'value':'31-2163', 'title': '31-2163'},
{'value':'8-749', 'title': '8-749'},
{'value':'8-955', 'title': '8-955'},
{'value':'8-981', 'title': '8-981'},
{'value':'8-773', 'title': '8-773'},
{'value':'8-927', 'title': '8-927'},
{'value':'8-947', 'title': '8-947'},
{'value':'8-776', 'title': '8-776'},
{'value':'8-810', 'title': '8-810'},
{'value':'8-793', 'title': '8-793'},
{'value':'31-2162', 'title': '31-2162'},
{'value':'8-775', 'title': '8-775'},
{'value':'8-862', 'title': '8-862'},
{'value':'31-2164', 'title': '31-2164'},
{'value':'8-957', 'title': '8-957'},
{'value':'8-926', 'title': '8-926'},
{'value':'8-974', 'title': '8-974'},
{'value':'8-977', 'title': '8-977'},
{'value':'8-988', 'title': '8-988'},
{'value':'8-943', 'title': '8-943'},
{'value':'8-928', 'title': '8-928'},
{'value':'8-956', 'title': '8-956'},
{'value':'8-777', 'title': '8-777'},
{'value':'8-861', 'title': '8-861'},
{'value':'8-973', 'title': '8-973'},
{'value':'8-976', 'title': '8-976'},
{'value':'45-2727', 'title': '45-2727'},
{'value':'8-863', 'title': '8-863'},
{'value':'8-975', 'title': '8-975'},
{'value':'8-987', 'title': '8-987'},
{'value':'8-958', 'title': '8-958'},
{'value':'8-989', 'title': '8-989'},
{'value':'8-978', 'title': '8-978'},
{'value':'31-1085', 'title': '31-1085'},
{'value':'31-1086', 'title': '31-1086'},
{'value':'31-751', 'title': '31-751'},
{'value':'8-9964', 'title': '8-9964'},
{'value':'31-762', 'title': '31-762'},
{'value':'8-3418', 'title': '8-3418'},
{'value':'8-2854', 'title': '8-2854'},
{'value':'17-86', 'title': '17-86'},
{'value':'8-225', 'title': '8-225'},
{'value':'8-149', 'title': '8-149'},
{'value':'8-1356', 'title': '8-1356'},
{'value':'8-50', 'title': '8-50'},
{'value':'8-151', 'title': '8-151'},
{'value':'8-1355', 'title': '8-1355'},
{'value':'45-63', 'title': '45-63'},
{'value':'8-220', 'title': '8-220'},
{'value':'8-2261', 'title': '8-2261'},
{'value':'45-2729', 'title': '45-2729'},
{'value':'8-574', 'title': '8-574'},
{'value':'45-132', 'title': '45-132'},
{'value':'8-3419', 'title': '8-3419'},
{'value':'8-242', 'title': '8-242'},
{'value':'45-2728', 'title': '45-2728'},
{'value':'8-406', 'title': '8-406'},
{'value':'8-211', 'title': '8-211'},
{'value':'8-191', 'title': '8-191'},
{'value':'8-390', 'title': '8-390'},
{'value':'8-3499', 'title': '8-3499'},
{'value':'45-135', 'title': '45-135'},
{'value':'45-136', 'title': '45-136'},
{'value':'8-598', 'title': '8-598'},
{'value':'8-190', 'title': '8-190'},
{'value':'8-193', 'title': '8-193'},
{'value':'8-599', 'title': '8-599'}
       ],

       "valueSources":[
          "value"
       ]
    },
      "Store ID":{
         "type":"select",
     "listValues":[{'value':'1', 'title': '1-SEATTLE'},
{'value':'2', 'title': '2-128 POST STREET'},
{'value':'3', 'title': '3-MINNEAPOLIS-CLOSED'},
{'value':'4', 'title': '4-CHICAGO'},
{'value':'5', 'title': '5-OUTLET SHOPS @ GETTYSBURG'},
{'value':'6', 'title': '6-BLOOR STREET (R6)'},
{'value':'6', 'title': '6-GRANDVIEW CORNERS OUTLET'},
{'value':'7', 'title': '7-KINGSWAY MALL (R7)'},
{'value':'9', 'title': '9-BELLEVUE SQUARE'},
{'value':'10', 'title': '10-WEST EDMONTON MALL (R10)'},
{'value':'11', 'title': '11-CALGARY (R11)'},
{'value':'12', 'title': '12-EDMONTON CITY CENTRE R12'},
{'value':'14', 'title': '14-HOUSTON PREMIUM OUTLET'},
{'value':'15', 'title': '15-OLD ORCHARD'},
{'value':'16', 'title': '16-OAKBROOK CENTER'},
{'value':'17', 'title': '17-PRIME OUTLET @ORLANDO R17'},
{'value':'18', 'title': '18-OSAGE BEACH OUTLET R18'},
{'value':'19', 'title': '19-KING OF PRUSSIA'},
{'value':'20', 'title': '20-HILLSDALE'},
{'value':'21', 'title': '21-SAN CLEMENTE'},
{'value':'22', 'title': '22-MARKET STREET'},
{'value':'23', 'title': '23-SOUTHDALE CENTER'},
{'value':'24', 'title': '24-WOODFIELD MALL'},
{'value':'25', 'title': '25-WOODLAND'},
{'value':'26', 'title': '26-CLACKAMAS TOWN CENTER'},
{'value':'27', 'title': '27-SOUTH COAST PLAZA'},
{'value':'28', 'title': '28-SOUTHWEST PLAZA'},
{'value':'29', 'title': '29-WILLOW GROVE'},
{'value':'30', 'title': '30-SHERWAY GARDENS (R30)'},
{'value':'31', 'title': '31-TYSONS CORNER'},
{'value':'32', 'title': '32-BEVERLY CENTER'},
{'value':'33', 'title': '33-BURLINGTON OUTLET R33'},
{'value':'34', 'title': '34-STAMFORD TOWN CENTER'},
{'value':'35', 'title': '35-AMERICAN DREAM WAY'},
{'value':'36', 'title': '36-SOMERSET COLLECTION'},
{'value':'37', 'title': '37-WHITE FLINT'},
{'value':'38', 'title': '38-LAS VEGAS OUTLET R38'},
{'value':'39', 'title': '39-HAWTHORN MALL'},
{'value':'40', 'title': '40-RIDGEDALE CENTER'},
{'value':'41', 'title': '41-SANTA MONICA'},
{'value':'42', 'title': '42-TWELVE OAKS MALL'},
{'value':'44', 'title': '44-MEDFORD OUTLET CENTER R44'},
{'value':'45', 'title': '45-WEST FARMS-CLOSED'},
{'value':'46', 'title': '46-VALLEY FAIR'},
{'value':'47', 'title': '47-LAKESIDE'},
{'value':'48', 'title': '48-CHRISTIANA MALL'},
{'value':'49', 'title': '49-CHERRY HILL'},
{'value':'50', 'title': '50-WESTFIELD MAIN PLACE'},
{'value':'51', 'title': '51-WESTFIELD SOUTHCENTER'},
{'value':'52', 'title': '52-NEWPORT CENTRE'},
{'value':'53', 'title': '53-STONESTOWN GALLERIA'},
{'value':'54', 'title': '54-HORTON PLAZA'},
{'value':'55', 'title': '55-FAIR OAKS MALL'},
{'value':'56', 'title': '56-TOWN CENTER CORTE MADERA'},
{'value':'57', 'title': '57-NORTHLAKE-CLOSED'},
{'value':'58', 'title': '58-SOUTHCENTER KIOSK-CLOSED'},
{'value':'59', 'title': '59-SUN VALLEY-CLOSED'},
{'value':'60', 'title': '60-FAIRLANE TOWN CENTER'},
{'value':'61', 'title': '61-STONERIDGE-CLOSED'},
{'value':'62', 'title': '62-BRIDGEWATER COMMONS R62'},
{'value':'63', 'title': '63-SOUTHCENTRE MALL (R63)'},
{'value':'64', 'title': '64-MAYFAIR'},
{'value':'65', 'title': '65-FRANKLIN PARK MALL'},
{'value':'66', 'title': '66-GLENDALE'},
{'value':'67', 'title': '67-WASHINGTON SQUARE'},
{'value':'68', 'title': '68-LAKE FOREST MALL-CLOSED'},
{'value':'69', 'title': '69-LA CUMBRE PLAZA'},
{'value':'70', 'title': '70-SOUTH HILLS VILLAGE'},
{'value':'71', 'title': '71-ROSS PARK MALL'},
{'value':'72', 'title': '72-GALLERIA AT ERIEVIEW'},
{'value':'73', 'title': '73-BURLINGTON MALL'},
{'value':'74', 'title': '74-SCARBOROUGH TWN CTR (R74)'},
{'value':'75', 'title': '75-FAIRVIEW MALL (R75)'},
{'value':'76', 'title': '76-BURNSVILLE CENTER'},
{'value':'77', 'title': '77-KEYSTONE AT THE CROSSING'},
{'value':'78', 'title': '78-WSTFLD UNIVERSITY TWN CTR'},
{'value':'79', 'title': '79-MONROEVILLE'},
{'value':'80', 'title': '80-AURORA-CLOSED'},
{'value':'81', 'title': '81-NORTHRIDGE-CLOSED'},
{'value':'82', 'title': '82-HOLYOKE RIDGE'},
{'value':'83', 'title': '83-CUMBERLAND-CLOSED'},
{'value':'84', 'title': '84-ALDERWOOD MALL'},
{'value':'85', 'title': '85-NORTHGATE MALL'},
{'value':'86', 'title': '86-OUTLETS OF DES MOINES'},
{'value':'88', 'title': '88-KENWOOD TOWN CENTER'},
{'value':'89', 'title': '89-PACIFIC CENTRE (R89)'},
{'value':'90', 'title': '90-SPOKANE VALLEY OUTLET R90'},
{'value':'91', 'title': '91-SACRAMENTO OUTLET (R91)'},
{'value':'92', 'title': '92-BRIARWOOD MALL'},
{'value':'93', 'title': '93-NORTHLAND MALL-CLOSED'},
{'value':'94', 'title': '94-CHESTERFIELD MALL'},
{'value':'95', 'title': '95-CROSSINGS OUTLET R95'},
{'value':'96', 'title': '96-THE GROVE AT SHREWSBURY'},
{'value':'97', 'title': '97-OLD ORCHARD'},
{'value':'98', 'title': '98-CRYSTAL MALL'},
{'value':'99', 'title': '99-MAINE MALL'},
{'value':'100', 'title': '100-CENTENNIAL POP UP'},
{'value':'101', 'title': '101-TANGER OUTLET @ COOKSTOWN'},
{'value':'102', 'title': '102-LEGACY PLACE'},
{'value':'103', 'title': '103-CORTE MADERA'},
{'value':'104', 'title': '104-WEST COUNTY CENTER'},
{'value':'105', 'title': '105-ROOSEVELT FIELD'},
{'value':'106', 'title': '106-ORLAND SQUARE'},
{'value':'107', 'title': '107-COLUMBUS CITY CENTER'},
{'value':'108', 'title': '108-VERNON HILLS'},
{'value':'109', 'title': '109-ROCKAWAY TOWN SQUARE'},
{'value':'110', 'title': '110-WESTGATE OUTLET'},
{'value':'111', 'title': '111-ANCHORAGE 5TH AVE MALL'},
{'value':'112', 'title': '112-WALDEN GALLERIA'},
{'value':'113', 'title': '113-POUGHKEEPSIE GALLERIA'},
{'value':'114', 'title': '114-PENTAGON'},
{'value':'115', 'title': '115-GARDEN STATE PLAZA'},
{'value':'116', 'title': '116-NORTHBROOK COURT'},
{'value':'117', 'title': '117-FASHION PLACE'},
{'value':'118', 'title': '118-SCOTTSDALE FASHION SQUARE'},
{'value':'119', 'title': '119-COLORADO MILLS WHSE STORE'},
{'value':'120', 'title': '120-NORTHWEST PLAZA'},
{'value':'121', 'title': '121-LAUREL PARK PLACE'},
{'value':'122', 'title': '122-VALLEY RIVER'},
{'value':'123', 'title': '123-NATICK MALL'},
{'value':'125', 'title': '125-CROSSGATES MALL'},
{'value':'126', 'title': '126-PALOS VERDES'},
{'value':'127', 'title': '127-ST. LOUIS UNION STATION'},
{'value':'128', 'title': '128-KENSINGTON VALLEY R128'},
{'value':'129', 'title': '129-METROPOLIS AT METROTOWN'},
{'value':'130', 'title': '130-IRONDEQUOIT MALL'},
{'value':'131', 'title': '131-BUCKLAND HILLS'},
{'value':'132', 'title': '132-RIDEAU CENTER (R132)'},
{'value':'133', 'title': '133-LANSING MALL'},
{'value':'134', 'title': '134-FIESTA MALL'},
{'value':'135', 'title': '135-ARDEN FAIR'},
{'value':'136', 'title': '136-MERIDIAN MALL'},
{'value':'137', 'title': '137-HULEN MALL'},
{'value':'138', 'title': '138-BREA MALL'},
{'value':'139', 'title': '139-PIONEER PLACE'},
{'value':'141', 'title': '141-EASTERN HILLS'},
{'value':'142', 'title': '142-SHOPS AT SADDLE CREEK'},
{'value':'143', 'title': '143-HOUSTON GALLERIA R143'},
{'value':'144', 'title': '144-ADIRONDACK OUTLET 144'},
{'value':'145', 'title': '145-SOUTHERN PARK'},
{'value':'146', 'title': '146-FASHION SQUARE'},
{'value':'147', 'title': '147-PERIMETER MALL'},
{'value':'148', 'title': '148-CHESTERFIELD TOWNE CENTER'},
{'value':'149', 'title': '149-SHOPS AT PIGEON FORGE'},
{'value':'150', 'title': '150-EAST TOWNE MALL'},
{'value':'151', 'title': '151-WEST TOWNE MALL'},
{'value':'152', 'title': '152-NORTH STAR MALL'},
{'value':'153', 'title': '153-LINCOLN CITY OUTLET (153)'},
{'value':'154', 'title': '154-HIGHLAND MALL'},
{'value':'155', 'title': '155-BOISE TOWNE SQUARE'},
{'value':'156', 'title': '156-SPRINGFIELD MALL'},
{'value':'157', 'title': '157-POTOMAC MILLS OUT (R157)'},
{'value':'158', 'title': '158-FASHION DIST PHILADELPHIA'},
{'value':'159', 'title': '159-ROSEDALE SHOPPING CENTER'},
{'value':'160', 'title': '160-GARDEN STATE PLAZA'},
{'value':'161', 'title': '161-GLENBROOK SQUARE'},
{'value':'162', 'title': '162-DESERT HILLS OUT (R162)'},
{'value':'163', 'title': '163-CITADEL OUTLET (R163)'},
{'value':'164', 'title': '164-GREAT MALL OF BAY AREA'},
{'value':'165', 'title': '165-BELLEVUE CENTER'},
{'value':'166', 'title': '166-CHRISTIANA MALL'},
{'value':'167', 'title': '167-LANDMARK CENTER'},
{'value':'168', 'title': '168-CORONADO CENTER'},
{'value':'169', 'title': '169-NANUET MALL'},
{'value':'170', 'title': '170-CHERRY CREEK NORTH'},
{'value':'171', 'title': '171-PARK ROYAL SHP CTR (R171)'},
{'value':'172', 'title': '172-SQUARE ONE (R172)'},
{'value':'173', 'title': '173-WHITE MARSH MALL'},
{'value':'174', 'title': '174-CAROUSEL MALL'},
{'value':'175', 'title': '175-THE MALL AT COLUMBIA'},
{'value':'176', 'title': '176-VALLEY VIEW CENTER'},
{'value':'177', 'title': '177-WESTFIELD FOX VALLEY'},
{'value':'178', 'title': '178-MAYFAIR SHOPPING CTR R178'},
{'value':'179', 'title': '179-ST. CHARLES TOWN CENTER'},
{'value':'180', 'title': '180-ZONE PRICING USFP'},
{'value':'200', 'title': '200-THE GARDENS'},
{'value':'201', 'title': '201-THE CROSSROADS'},
{'value':'202', 'title': '202-TRI-COUNTY MALL'},
{'value':'203', 'title': '203-SOUTHGLENN MALL'},
{'value':'204', 'title': '204-OAKRIDGE MALL'},
{'value':'205', 'title': '205-OAKLAND MALL'},
{'value':'206', 'title': '206-NORTHRIDGE MALL'},
{'value':'207', 'title': '207-LAKESIDE SHOPPING CTR'},
{'value':'208', 'title': '208-HANES MALL'},
{'value':'209', 'title': '209-TOWN CENTER AT BOCA RATON'},
{'value':'210', 'title': '210-THE ESPLANADE'},
{'value':'211', 'title': '211-HAMILTON EATON CNTR(R211)'},
{'value':'212', 'title': '212-RIVERWALK MARKET PLACE'},
{'value':'213', 'title': '213-FASHION VALLEY'},
{'value':'214', 'title': '214-OUTLET SHOPS@OSHKOSH R214'},
{'value':'215', 'title': '215-THE PINNACLE'},
{'value':'216', 'title': '216-TEMP - THE CROSSINGS R95'},
{'value':'217', 'title': '217-NEBRASKA CROSSINGS OTLTS'},
{'value':'218', 'title': '218-GLOUCESTER PREMIUM OUTLET'},
{'value':'219', 'title': '219-SEASIDE FACTORY OTLT 219'},
{'value':'220', 'title': '220-CRABTREE VALLEY MALL'},
{'value':'221', 'title': '221-MARKVILLE SHP CTR (R221)'},
{'value':'222', 'title': '222-SAN LEANDRO OUTLET (222)'},
{'value':'223', 'title': '223-WILLIAMSBURG OUTLET'},
{'value':'224', 'title': '224-OTLT SHOPPE OF BLUEGRASS'},
{'value':'225', 'title': '225-HILTON HEAD OUTLET (R225)'},
{'value':'226', 'title': '226-TWIN CITIES AT EAGAN OTLT'},
{'value':'227', 'title': '227-FOUR SEASONS TOWN CENTRE'},
{'value':'228', 'title': '228-ROBSON STREET'},
{'value':'229', 'title': '229-SOUTHPARK MALL'},
{'value':'230', 'title': '230-BEACHWOOD PLACE'},
{'value':'231', 'title': '231-LAKE AVENUE'},
{'value':'232', 'title': '232-100 FIFTH AVENUE'},
{'value':'233', 'title': '233-VAUGHAN MILLS R233'},
{'value':'234', 'title': '234-LEE PREMIUM OUTLETS'},
{'value':'235', 'title': '235-LINCOLN PLACE'},
{'value':'236', 'title': '236-ST AUGUSTINE PREMIUM OUTL'},
{'value':'237', 'title': '237-NEW MARKET OUTLET R237'},
{'value':'238', 'title': '238-REHOBOTH OUTLET (R238)'},
{'value':'239', 'title': '239-MARLEY STATION'},
{'value':'240', 'title': '240-SUGARLOAF MILLS 240'},
{'value':'242', 'title': '242-SILVER SANDS FCTY STORES'},
{'value':'243', 'title': '243-OUTLETS AT WEST BRANCH'},
{'value':'244', 'title': '244-CAROLINA OUTLET R244'},
{'value':'245', 'title': '245-OUTLETS AT TRAVERSE MTN'},
{'value':'246', 'title': '246-CHESHIRE OUTLET'},
{'value':'247', 'title': '247-MANCHESTER DESIGNER OUTLT'},
{'value':'248', 'title': '248-OTLT SHOPS OF GRAND RIVER'},
{'value':'249', 'title': '249-BOISE FACTORY OUTLET R249'},
{'value':'250', 'title': '250-MEADOWOOD MALL'},
{'value':'251', 'title': '251-SAINT LOUIS GALLERIA'},
{'value':'252', 'title': '252-WILLOWBROOK MALL'},
{'value':'253', 'title': '253-GILROY OUTLET R253'},
{'value':'254', 'title': '254-LIGHTHOUSE PL OUT (R254)'},
{'value':'255', 'title': '255-BIRCH RUN OUTLET (R255)'},
{'value':'256', 'title': '256-BEND FACTORY OUT (R256)'},
{'value':'259', 'title': '259-CROSSROAD SHOPPING CENTER'},
{'value':'260', 'title': '260-NORTHGLENN OUTLET R260'},
{'value':'261', 'title': '261-ARENA HUB OUTLET R261'},
{'value':'262', 'title': '262-NOVATO OUTLET R262'},
{'value':'263', 'title': '263-SETTLERS GREEN OUTLET 263'},
{'value':'264', 'title': '264-OUT COLLECTION AT NIAGARA'},
{'value':'265', 'title': '265-WESTLAND CNTR OUTLET R265'},
{'value':'266', 'title': '266-NORTHWAY MALL OUTLET R266'},
{'value':'268', 'title': '268-SANTA FE OUTLET R268'},
{'value':'269', 'title': '269-THE OUTLETS @ ZION R269'},
{'value':'270', 'title': '270-CARY VILLAGE MALL'},
{'value':'271', 'title': '271-SMITHAVEN MALL'},
{'value':'272', 'title': '272-MALL AT GREEN HILLS'},
{'value':'273', 'title': '273-REGENCY SQUARE'},
{'value':'274', 'title': '274-KITTERY/MAINE GATE MALL'},
{'value':'276', 'title': '276-CAMARILLO OUTLET R276'},
{'value':'277', 'title': '277-JERSEY SHORE OUTLET R277'},
{'value':'278', 'title': '278-AURORA PREMIUM R278'},
{'value':'279', 'title': '279-NORTH COUNTY FAIR'},
{'value':'280', 'title': '280-LAKE BUENA VISTA FAC STR'},
{'value':'281', 'title': '281-LAS AMERICAS OUTLET R281'},
{'value':'283', 'title': '283-FOX RIVER'},
{'value':'284', 'title': '284-TOWSON TOWN CENTER'},
{'value':'285', 'title': '285-HILLSBORO OUTLET (R285)'},
{'value':'288', 'title': '288-LLOYD CENTER R288'},
{'value':'290', 'title': '290-VILLAGE @ GARDEN CITY CTR'},
{'value':'291', 'title': '291-MALL OF AMERICA'},
{'value':'293', 'title': '293-PREFERRED OUTLET @ TULARE'},
{'value':'294', 'title': '294-OAKPARK MALL'},
{'value':'295', 'title': '295-OXMORE CENTER'},
{'value':'296', 'title': '296-ZCMI CENTER'},
{'value':'298', 'title': '298-BELDEN VILLAGE'},
{'value':'299', 'title': '299-MONTCLAIR PLAZA'},
{'value':'300', 'title': '300-BRIDGEHAMPTON'},
{'value':'301', 'title': '301-FOX RIVER MALL'},
{'value':'302', 'title': '302-WESTPORT'},
{'value':'304', 'title': '304-MILL STREET PLAZA'},
{'value':'306', 'title': '306-LOUISIANA BOARDWALK'},
{'value':'307', 'title': '307-SOUTH PLAINS MALL'},
{'value':'308', 'title': '308-ROUND ROCK OUTLET R308'},
{'value':'309', 'title': '309-WOODLAND HILLS'},
{'value':'310', 'title': '310-COUNTRY CLUB PLAZA'},
{'value':'311', 'title': '311-OUTLET AT THE DELLS'},
{'value':'313', 'title': '313-CHICAGO PREMIUM OUTLET'},
{'value':'314', 'title': '314-SILVERDALE OUTLET (R314)'},
{'value':'315', 'title': '315-COLLIN CREEK MALL'},
{'value':'317', 'title': '317-PENN SQUARE'},
{'value':'318', 'title': '318-NORTHPARK MALL'},
{'value':'319', 'title': '319-GOVERNORS SQUARE'},
{'value':'320', 'title': '320-SANTA ROSA PLAZA'},
{'value':'321', 'title': '321-ONE PACIFIC PLACE'},
{'value':'322', 'title': '322-MERIDEN SQUARE'},
{'value':'323', 'title': '323-PARK PLAZA'},
{'value':'324', 'title': '324-CHARLESTON OUTLET R324'},
{'value':'325', 'title': '325-THE CITADEL'},
{'value':'326', 'title': '326-VALLEY WEST MALL'},
{'value':'327', 'title': '327-BELLEVUE SQUARE 2ND LEVEL'},
{'value':'328', 'title': '328-ALAMANCE R328'},
{'value':'329', 'title': '329-TACOMA MALL'},
{'value':'330', 'title': '330-THE OAKS SHOPPING CENTER'},
{'value':'331', 'title': '331-TOWN CENTER AT COBB'},
{'value':'332', 'title': '332-RIVERCHASE GALLERIA'},
{'value':'333', 'title': '333-MONTGOMERY MALL'},
{'value':'334', 'title': '334-DESTINY USA R334'},
{'value':'336', 'title': '336-MALL AT FAIRFIELD COMMONS'},
{'value':'337', 'title': '337-BATTLEFIELD MALL'},
{'value':'338', 'title': '338-COLUMBIANA MALL'},
{'value':'339', 'title': '339-DEL MONTE SHOPPING CTR'},
{'value':'340', 'title': '340-GALLERIA AT CRYSTAL RUN'},
{'value':'341', 'title': '341-WEST TOWN MALL'},
{'value':'342', 'title': '342-PEACHTREE MALL'},
{'value':'343', 'title': '343-ARROWHEAD TOWNE CENTER'},
{'value':'344', 'title': '344-SILVER CITY GALLERIA'},
{'value':'345', 'title': '345-PLACE DORLEANS (R345)'},
{'value':'346', 'title': '346-THE MALL AT STEAMTOWN'},
{'value':'347', 'title': '347-NORTH POINT MALL'},
{'value':'348', 'title': '348-ASPEN PLACE @ THE SAWMILL'},
{'value':'349', 'title': '349-DOWNTOWN PLAZA'},
{'value':'350', 'title': '350-VALENCIA TOWN CENTER'},
{'value':'351', 'title': '351-PHILADELPHIA PREMIUM'},
{'value':'352', 'title': '352-SUNRISE MALL'},
{'value':'353', 'title': '353-DAYTON MALL'},
{'value':'354', 'title': '354-SALEM CENTRE'},
{'value':'355', 'title': '355-NATICK MALL'},
{'value':'356', 'title': '356-TANGER @ PITTSBURGH R356'},
{'value':'357', 'title': '357-BAYBROOK MALL'},
{'value':'358', 'title': '358-ACADIANA MALL'},
{'value':'359', 'title': '359-ANNAPOLIS MALL'},
{'value':'360', 'title': '360-ARCHES @ DEER PARK R360'},
{'value':'361', 'title': '361-BERKSHIRE MALL'},
{'value':'362', 'title': '362-PYRAMID MALL'},
{'value':'363', 'title': '363-SALMON RUN'},
{'value':'364', 'title': '364-SANGERTOWN SQUARE'},
{'value':'365', 'title': '365-TUCSON MALL'},
{'value':'366', 'title': '366-WEST OAKS MALL'},
{'value':'367', 'title': '367-THE WOODLANDS MALL'},
{'value':'368', 'title': '368-SOUTH SQUARE MALL'},
{'value':'369', 'title': '369-HICKORY HOLLOW MALL'},
{'value':'370', 'title': '370-COLUMBIA GORGE OUTLET'},
{'value':'371', 'title': '371-RIVERGATE MALL'},
{'value':'372', 'title': '372-SEATTLE PREMIUM OUTL R372'},
{'value':'373', 'title': '373-NORTHWOODS MALL'},
{'value':'374', 'title': '374-GENESEE VALLEY CENTER'},
{'value':'375', 'title': '375-THE BRADLEY FAIR'},
{'value':'376', 'title': '376-WESTGATE MALL'},
{'value':'377', 'title': '377-THE PARKS AT ARLINGTON'},
{'value':'378', 'title': '378-NORTH GRAND MALL'},
{'value':'379', 'title': '379-RIMROCK MALL'},
{'value':'380', 'title': '380-LINDALE'},
{'value':'381', 'title': '381-PLEASANT PRAIRIE OUTLET'},
{'value':'382', 'title': '382-PRIME @ HUNTLEY (R 382)'},
{'value':'383', 'title': '383-RIO GRANDE VALLEY OUTLET'},
{'value':'384', 'title': '384-EASTLAND MALL'},
{'value':'385', 'title': '385-FOOTHILLS FASHION MALL'},
{'value':'386', 'title': '386-FCTRY ST. @ PRK CTY(R386'},
{'value':'387', 'title': '387-ST LOUIS PREMIUM OUTLETS'},
{'value':'388', 'title': '388-COOL SPRINGS GALLERIA'},
{'value':'389', 'title': '389-ROGUE VALLEY MALL'},
{'value':'390', 'title': '390-CHERRYVALE MALL'},
{'value':'391', 'title': '391-ASHEVILLE MALL'},
{'value':'392', 'title': '392-BELLIS FAIR MALL'},
{'value':'393', 'title': '393-COLUMBIA MALL'},
{'value':'394', 'title': '394-CRESTWOOD PLAZA'},
{'value':'395', 'title': '395-FLAGSTAFF MALL'},
{'value':'396', 'title': '396-OAKDALE MALL'},
{'value':'397', 'title': '397-OAKWOOD MALL'},
{'value':'398', 'title': '398-OGLETHORPE MALL'},
{'value':'399', 'title': '399-PARADISE VALLEY'},
{'value':'400', 'title': '400-RUSHMORE MALL'},
{'value':'401', 'title': '401-VALLEY VIEW MALL'},
{'value':'402', 'title': '402-WESTDALE MALL'},
{'value':'403', 'title': '403-WHITE OAKS MALL'},
{'value':'404', 'title': '404-MIDTOWN PLAZA (R404)'},
{'value':'405', 'title': '405-COQUITLAM CENTRE (R405)'},
{'value':'406', 'title': '406-MIC MAC MALL (R406)'},
{'value':'407', 'title': '407-OHIO FACTORY SHOPS (407)'},
{'value':'408', 'title': '408-TIPPECANOE MALL'},
{'value':'409', 'title': '409-ATLANTIC CITY OUTLET R409'},
{'value':'410', 'title': '410-STATE COLLEGE'},
{'value':'411', 'title': '411-68TH & THIRD AVE'},
{'value':'412', 'title': '412-GOVERNMENT STREET (R412)'},
{'value':'414', 'title': '414-INDIANA PREMIUM OUTLETS'},
{'value':'415', 'title': '415-EATON PLACE (R415)'},
{'value':'416', 'title': '416-BROADWAY'},
{'value':'417', 'title': '417-STATION MALL (R417)'},
{'value':'421', 'title': '421-NIAGARA FALLS OUTLET (421'},
{'value':'422', 'title': '422-TANGER AT NATIONAL HARBOR'},
{'value':'423', 'title': '423-CENTRALIA OUTLET R423'},
{'value':'424', 'title': '424-APACHE MALL'},
{'value':'425', 'title': '425-BRANDON TOWN CENTER'},
{'value':'426', 'title': '426-COLLEGE MALL'},
{'value':'427', 'title': '427-UNIVERSITY VILLAGE'},
{'value':'429', 'title': '429-QUEENSTOWN OUTLET R429'},
{'value':'431', 'title': '431-GEORGETOWN'},
{'value':'432', 'title': '432-CIRCLE CENTRE'},
{'value':'433', 'title': '433-LINCOLN TRIANGLE'},
{'value':'434', 'title': '434-THE WESTCHESTER'},
{'value':'435', 'title': '435-LYNNHAVEN MALL'},
{'value':'436', 'title': '436-COTTONWOOD MALL'},
{'value':'437', 'title': '437-GAFFNEY OUTLET R437'},
{'value':'438', 'title': '438-TANGER OUTLET @ COMMERCE'},
{'value':'439', 'title': '439-HOLIDAY VILLAGE'},
{'value':'440', 'title': '440-MONTGOMERY MALL'},
{'value':'441', 'title': '441-POST OAK MALL'},
{'value':'442', 'title': '442-SOUTH HILL MALL'},
{'value':'443', 'title': '443-SOUTHGATE MALL'},
{'value':'444', 'title': '444-THE GALLERIA AT SUNSET'},
{'value':'445', 'title': '445-VILLAGE ARCADE'},
{'value':'448', 'title': '448-OUTLET COLLECTION SEATTLE'},
{'value':'449', 'title': '449-HAMILTON PLACE'},
{'value':'450', 'title': '450-NORTHPARK MALL R450'},
{'value':'451', 'title': '451-OXFORD VALLEY MALL'},
{'value':'452', 'title': '452-TANGER OTLT AT FOXWOODS'},
{'value':'454', 'title': '454-WHISTLER VILLAGE (R454)'},
{'value':'456', 'title': '456-EASTVIEW MALL'},
{'value':'458', 'title': '458-NEZ PERCE OUTLET R458'},
{'value':'459', 'title': '459-CORTANA MALL'},
{'value':'460', 'title': '460-THE JOHNSTOWN GALLERIA'},
{'value':'461', 'title': '461-WEST ACRES SHOPPING CENTE'},
{'value':'463', 'title': '463-SHASTA OUTLET R463'},
{'value':'464', 'title': '464-MIROMAR OUTLET R464'},
{'value':'465', 'title': '465-CHARLESTON TOWN CENTER'},
{'value':'466', 'title': '466-FRIENFDLY SHOPPING CENTER'},
{'value':'467', 'title': '467-SOUTHLAKE MALL'},
{'value':'468', 'title': '468-POLO PARK (R468)'},
{'value':'469', 'title': '469-WHSE STORE - COL DC'},
{'value':'470', 'title': '470-SALVAGE STORE - COL DC'},
{'value':'471', 'title': '471-TANGER OUTLETS OCEAN CITY'},
{'value':'472', 'title': '472-GATEWAY MALL'},
{'value':'473', 'title': '473-COLUMBIA CENTER'},
{'value':'474', 'title': '474-UNIVERSITY PARK'},
{'value':'475', 'title': '475-VALLEY MALL OUTLET R475'},
{'value':'477', 'title': '477-NAGS HEAD OUTLET R477'},
{'value':'478', 'title': '478-MARKET ST @ WOODLANDS'},
{'value':'479', 'title': '479-PRESTON PARK R479'},
{'value':'482', 'title': '482-PINNACLE HILLS R482'},
{'value':'483', 'title': '483-STONECREEK VILLAGE R483'},
{'value':'484', 'title': '484-LENOX SQUARE'},
{'value':'485', 'title': '485-VILLAGE AT TOPANGA'},
{'value':'486', 'title': '486-QUAKER BRIDGE MALL'},
{'value':'487', 'title': '487-CHINOOK CENTRE (R487)'},
{'value':'488', 'title': '488-KANSAS CITY FCT OUT.(488)'},
{'value':'489', 'title': '489-RESTON TOWN CENTER'},
{'value':'492', 'title': '492-ORLANDO PREMIUM OUTLETS'},
{'value':'493', 'title': '493-OAKRIDGE CENTRE (R493)'},
{'value':'495', 'title': '495-TILTON OUTLET R495'},
{'value':'496', 'title': '496-SILVERTHORNE FCTRY (R496)'},
{'value':'497', 'title': '497-GROVE CITY FACTORY (R497)'},
{'value':'498', 'title': '498-TANGER OTLTS AT CHARLOTTE'},
{'value':'499', 'title': '499-TORONTO PREMIUM OUT R499'},
{'value':'500', 'title': '500-CACHE STREET (R500)'},
{'value':'501', 'title': '501-DEPTFORD MALL (R501)'},
{'value':'502', 'title': '502-HERITAGE SQUARE R502'},
{'value':'503', 'title': '503-NW ARKANSAS MALL (R503)'},
{'value':'504', 'title': '504-PARK MEADOWS TOWN CTR SPR'},
{'value':'507', 'title': '507-MICHIGAN AVE SPRT (R507)'},
{'value':'510', 'title': '510-SOUTHPARK CENTER (R510)'},
{'value':'515', 'title': '515-CF CHAMPLAIN'},
{'value':'516', 'title': '516-KIRKWOOD MALL (R516)'},
{'value':'517', 'title': '517-PARK CITY(R517)'},
{'value':'518', 'title': '518-VALLEY VIEW MALL'},
{'value':'519', 'title': '519-NORTHTOWN MALL'},
{'value':'520', 'title': '520-SHOPS AT DON MILLS'},
{'value':'523', 'title': '523-COLUMBIA MALL'},
{'value':'524', 'title': '524-GREENVILLE MALL'},
{'value':'525', 'title': '525-PHEASANT LANE MALL'},
{'value':'526', 'title': '526-SOLOMON POND MALL R526'},
{'value':'527', 'title': '527-VANCOUVER MALL'},
{'value':'528', 'title': '528-STREETS @INDIAN LAKE R528'},
{'value':'529', 'title': '529-SUMMIT MALL (R529)'},
{'value':'530', 'title': '530-SOUTH SHORE PLAZA (R530)'},
{'value':'531', 'title': '531-TRUMBULL (R531)'},
{'value':'532', 'title': '532-SOUTH PARK MALL (R532)'},
{'value':'533', 'title': '533-CHURCH STREET (R533)'},
{'value':'534', 'title': '534-YAKIMA MALL (R534)'},
{'value':'535', 'title': '535-WEST OAKS MALL (R535)'},
{'value':'543', 'title': '543-WOLFCHASE GALLERIA (R543)'},
{'value':'544', 'title': '544-LEHIGH VALLEY MALL (R544)'},
{'value':'545', 'title': '545-MEADOWS @ LAKE ST LOUIS'},
{'value':'546', 'title': '546-SHATTUCK AVENUE (R546)'},
{'value':'547', 'title': '547-MAIN PLACE R547'},
{'value':'558', 'title': '558-ZONE PRICING CAOUT'},
{'value':'580', 'title': '580-ZONE PRICING CAFP'},
{'value':'582', 'title': '582-ACCUM R405 COQ'},
{'value':'583', 'title': '583-ACCUM R454 WHI'},
{'value':'636', 'title': '636-MID-RIVERS MALL'},
{'value':'650', 'title': '650-SOUTHERN HILLS MALL'},
{'value':'651', 'title': '651-REDMOND TOWN CENTER(SPRT)'},
{'value':'654', 'title': '654-PALISADES CENTER (SPRT)'},
{'value':'657', 'title': '657-MENLO PARK (SPRT)'},
{'value':'659', 'title': '659-MACON MALL'},
{'value':'660', 'title': '660-MONMOUTH MALL'},
{'value':'661', 'title': '661-SOUTH TOWNE CENTER'},
{'value':'662', 'title': '662-THE EMPIRE'},
{'value':'663', 'title': '663-WEST RIDGE MALL'},
{'value':'664', 'title': '664-TUTTLE CROSSING (SPRT)'},
{'value':'667', 'title': '667-AUGUSTA MALL'},
{'value':'668', 'title': '668-BARTON CREEK SQUARE'},
{'value':'669', 'title': '669-OXMOOR CENTER R669'},
{'value':'670', 'title': '670-PORT PLAZA MALL'},
{'value':'671', 'title': '671-THE AVENUES'},
{'value':'672', 'title': '672-BOWER PLACE R672'},
{'value':'673', 'title': '673-FINGER LAKES OUTLET(R673)'},
{'value':'674', 'title': '674-GREAT PLAINS OUTLET(R674)'},
{'value':'675', 'title': '675-VAUGHAN WHSE STORE'},
{'value':'676', 'title': '676-FAYETTE MALL'},
{'value':'677', 'title': '677-MALL OF LOUISIANA'},
{'value':'678', 'title': '678-MALL OF NEW HAMPSHIRE'},
{'value':'679', 'title': '679-CHAPEL HILLS MALL'},
{'value':'680', 'title': '680-RIVER PARK SQUARE'},
{'value':'681', 'title': '681-COLUMBIA MALL'},
{'value':'682', 'title': '682-SOUTH SHORE PLAZA'},
{'value':'683', 'title': '683-CORNWALL SHOPPING CENTRE'},
{'value':'684', 'title': '684-SOUTHGATE CENTRE (R684)'},
{'value':'689', 'title': '689-THE SUMMIT R689'},
{'value':'690', 'title': '690-TROLLEY SQUARE'},
{'value':'691', 'title': '691-CORDOVA MALL'},
{'value':'692', 'title': '692-SARATOGA SPRINGS (R-692)'},
{'value':'693', 'title': '693-WILLOWBROOK MALL'},
{'value':'696', 'title': '696-SEMINOLE TOWN CENTER'},
{'value':'697', 'title': '697-WHITE OAKS MALL (R697)'},
{'value':'698', 'title': '698-CAPITOL PROMENADE R698'},
{'value':'699', 'title': '699-CAROLINA PLACE'},
{'value':'700', 'title': '700-WEST PARK MALL (R700)'},
{'value':'701', 'title': '701-WHISTLER VILLAGE'},
{'value':'702', 'title': '702-FRONTIER MALL (R702)'},
{'value':'703', 'title': '703-BAYSHORE SHOPNG CTR(R703'},
{'value':'704', 'title': '704-CROSSROADS CENTER (R704)'},
{'value':'705', 'title': '705-OAK VIEW MALL (R705)'},
{'value':'706', 'title': '706-BEL AIR MALL (R706)'},
{'value':'707', 'title': '707-THE SHOPS @ BLACKHAWK(707'},
{'value':'708', 'title': '708-FIRST COLONY MALL (R708)'},
{'value':'709', 'title': '709-QUAIL SPRINGS MALL (R709)'},
{'value':'710', 'title': '710-MADISON SQUARE MALL(R710)'},
{'value':'711', 'title': '711-SOUTHGATE PLAZA (R711)'},
{'value':'712', 'title': '712-SIGNAL HILL OUTLET'},
{'value':'713', 'title': '713-MCCAIN MALL (R713)'},
{'value':'714', 'title': '714-MONTGOMERY MALL (R714)'},
{'value':'715', 'title': '715-KENNEDY MALL (R715)'},
{'value':'716', 'title': '716-BRASS MILL CENTER (R716)'},
{'value':'717', 'title': '717-EASTLAND MALL (R717)'},
{'value':'719', 'title': '719-TOWN WEST SQUARE'},
{'value':'720', 'title': '720-KNOXVILLE CENTER (R720)'},
{'value':'721', 'title': '721-MIDLAND PARK (R721)'},
{'value':'722', 'title': '722-VISTA RIDGE (R722)'},
{'value':'723', 'title': '723-INTERCITY SHPNG CTR(R723)'},
{'value':'724', 'title': '724-CASTLE ROCK FACTORY(R724)'},
{'value':'730', 'title': '730-THE GARDENS ON EL PASEO'},
{'value':'731', 'title': '731-BROADWAY POINT (R731)'},
{'value':'734', 'title': '734-CHEVY CHASE(R734)'},
{'value':'737', 'title': '737-JOHNSON CREEK OUTLET(R737'},
{'value':'738', 'title': '738-THE SHOPS AT RIVERWOODS'},
{'value':'739', 'title': '739-GREENWOOD PARK MALL'},
{'value':'740', 'title': '740-NEWGATE MALL'},
{'value':'741', 'title': '741-GREAT NORTHERN MALL'},
{'value':'742', 'title': '742-HIGHLAND COMMONS (R742)'},
{'value':'743', 'title': '743-NORTHSHORE MALL (743)'},
{'value':'746', 'title': '746-ALA MOANA CENTER (746)'},
{'value':'747', 'title': '747-SHOPS AT PARK LANE'},
{'value':'752', 'title': '752-CORAL RIDGE MALL'},
{'value':'753', 'title': '753-INDEPENDENCE CENTER (753)'},
{'value':'754', 'title': '754-MUNCIE MALL'},
{'value':'755', 'title': '755-EVERETT MALL (755)'},
{'value':'756', 'title': '756-MILLER HILL MALL'},
{'value':'757', 'title': '757-CAPITAL CITY MALL (757)'},
{'value':'758', 'title': '758-GRAND TETON MALL'},
{'value':'759', 'title': '759-FAYETTE MALL'},
{'value':'760', 'title': '760-JEFFERSON VALLEY MALL 760'},
{'value':'761', 'title': '761-LOGAN VALLEY MALL (761)'},
{'value':'762', 'title': '762-FLORENCE MALL'},
{'value':'763', 'title': '763-GREAT LAKES CROSSING(R763'},
{'value':'764', 'title': '764-MYRTLE BEACH FCT STR R764'},
{'value':'768', 'title': '768-LEBANON OUTLET (R768)'},
{'value':'769', 'title': '769-SANTA ANITA FASHION PARK'},
{'value':'770', 'title': '770-MOCK STORE-WILLOW RD'},
{'value':'774', 'title': '774-LIBERTY CENTER'},
{'value':'775', 'title': '775-HUEBNER OAKS (R775)'},
{'value':'776', 'title': '776-LOS CERRITOS CENTER (776)'},
{'value':'777', 'title': '777-AVALON MALL'},
{'value':'779', 'title': '779-SOUTHRIDGE MALL'},
{'value':'780', 'title': '780-CASTLETON SQUARE (R780)'},
{'value':'781', 'title': '781-MALL AT ROCKINGHAM PARK'},
{'value':'782', 'title': '782-FIG GARDEN VILLAGE (R782)'},
{'value':'783', 'title': '783-CIELO VISTA MALL (783)'},
{'value':'784', 'title': '784-GRAND TRAVERSE MALL (784)'},
{'value':'785', 'title': '785-DAKOTA SQUARE'},
{'value':'786', 'title': '786-LEGENDS OUTLET'},
{'value':'787', 'title': '787-CITRUS PARK TOWN CENTER'},
{'value':'789', 'title': '789-HAGERSTOWN OUTLET-(R789)'},
{'value':'790', 'title': '790-TANGER OUTLET @ OTTAWA'},
{'value':'791', 'title': '791-SOUTHLAKE TOWN SQUARE'},
{'value':'792', 'title': '792-BROADWAY SQUARE'},
{'value':'793', 'title': '793-ANNAPOLIS MALL'},
{'value':'795', 'title': '795-OUTLET SHOPPES AT ATLANTA'},
{'value':'798', 'title': '798-LINCOLN PARK'},
{'value':'799', 'title': '799-PROVIDENCE PLACE (799)'},
{'value':'802', 'title': '802-MACARTHUR CENTER (802)'},
{'value':'803', 'title': '803-RIVERTOWN CROSSING (803)'},
{'value':'804', 'title': '804-DULLES TOWN CENTER (804)'},
{'value':'805', 'title': '805-VALLEY MALL (805)'},
{'value':'806', 'title': '806-RIDGEMAR MALL (806)'},
{'value':'807', 'title': '807-WRENTHAM VILLAGE PREMIUM'},
{'value':'808', 'title': '808-EASTON TOWN CENTER'},
{'value':'809', 'title': '809-CAPE COD MALL (809)'},
{'value':'811', 'title': '811-MISSION VIEJO'},
{'value':'813', 'title': '813-MARKETPLACE SHOPPING CTR'},
{'value':'815', 'title': '815-WOODBURY COMMONS(R815)'},
{'value':'816', 'title': '816-FLORIDA MALL'},
{'value':'817', 'title': '817-WOODBURN COMPANY STR(R817'},
{'value':'818', 'title': '818-WOODINVILLE CENTER(R818)'},
{'value':'822', 'title': '822-YORKDALE SHOPPING CENTER'},
{'value':'823', 'title': '823-JOLIET COMMONS(R823)'},
{'value':'824', 'title': '824-GALLATIN VALLEY MALL'},
{'value':'825', 'title': '825-MALL OF GEORGIA'},
{'value':'826', 'title': '826-OUTLET @ ALBERTVILLE R826'},
{'value':'827', 'title': '827-OSHAWA MALL (827)'},
{'value':'828', 'title': '828-DESERT PASSAGE AT ALLADIN'},
{'value':'829', 'title': '829-DANBURY FAIR MALL R829'},
{'value':'831', 'title': '831-BOULEVARD MALL'},
{'value':'832', 'title': '832-TANGER OUTLETS AT BRANSON'},
{'value':'833', 'title': '833-CHARLESTOWNE MALL'},
{'value':'834', 'title': '834-ROOKWOOD COMMONS'},
{'value':'835', 'title': '835-UNIVERSITY MALL'},
{'value':'836', 'title': '836-643 MASSACHUSETTS STREET'},
{'value':'837', 'title': '837-EXTON SQUARE'},
{'value':'838', 'title': '838-N GEORGIA PREMIUM(R838)'},
{'value':'843', 'title': '843-GALLERIA @ ROSEVILLE R843'},
{'value':'844', 'title': '844-SOONER MALL R844'},
{'value':'845', 'title': '845-STONEBRIAR CENTRE (R845)'},
{'value':'846', 'title': '846-FIVE OAKS OUTLET(R846)'},
{'value':'850', 'title': '850-CONCORD MILLS(R850)'},
{'value':'851', 'title': '851-7000 AUSTIN ST'},
{'value':'852', 'title': '852-BENTLEY MALL'},
{'value':'853', 'title': '853-WENATCHEE VALLEY MALL'},
{'value':'855', 'title': '855-MILLCREEK MALL'},
{'value':'856', 'title': '856-PARK MALL R856'},
{'value':'857', 'title': '857-MASONVILLE PLACE'},
{'value':'860', 'title': '860-FLATIRON CROSSING R860'},
{'value':'864', 'title': '864-THE PROMENADE R864'},
{'value':'867', 'title': '867-VACAVILLE OUTLET (R-867)'},
{'value':'868', 'title': '868-GURNEE MILLS'},
{'value':'869', 'title': '869-BRINTON LAKE (R-869)'},
{'value':'870', 'title': '870-BANGOR MALL (R-870)'},
{'value':'871', 'title': '871-LEESBURG OUTLET (R-871)'},
{'value':'872', 'title': '872-ARUNDEL MILLS OUTLET R872'},
{'value':'873', 'title': '873-BOSTON OUTLET (R-873)'},
{'value':'874', 'title': '874-LANCASTER OUTLET R-874'},
{'value':'875', 'title': '875-SAN MARCOS OUTLET R-875'},
{'value':'876', 'title': '876-DEER PARK (R-876)'},
{'value':'881', 'title': '881-TSAWWASSEN (R881)'},
{'value':'882', 'title': '882-VIEJAS OUTLET CENTER R882'},
{'value':'884', 'title': '884-TANGER OUTLETS RIVERHEAD'},
{'value':'885', 'title': '885-VILLAGE PLAZA OUTLET R885'},
{'value':'886', 'title': '886-BIRCH ST. PROMENADE R-886'},
{'value':'887', 'title': '887-FOLSOM FACTORY OUTLET 887'},
{'value':'888', 'title': '888-ALLEN PREMIUM OUTLET R888'},
{'value':'889', 'title': '889-ARIZONA MILLS R-889'},
{'value':'891', 'title': '891-MALL OF THE BAY AREA R891'},
{'value':'892', 'title': '892-TANGER OUT-WILLIAMSBURG'},
{'value':'893', 'title': '893-TANGER OUTLET @ FOLEY 893'},
{'value':'894', 'title': '894-OHIO STATION OUTLET'},
{'value':'895', 'title': '895-NORTH BEND OUTLET R-895'},
{'value':'896', 'title': '896-AUGUSTA OUTLET R-896'},
{'value':'897', 'title': '897-WESTBROOK OUTLET R-897'},
{'value':'898', 'title': '898-BANDERA POINTE OUTLET 898'},
{'value':'899', 'title': '899-SUMMITWOODS OUTLET R-899'},
{'value':'902', 'title': '902-SOUTHWEST PLAZA R-902'},
{'value':'903', 'title': '903-CHARLOTTESVILLE FS (R903)'},
{'value':'907', 'title': '907-GREELEY MALL R-907'},
{'value':'908', 'title': '908-YORKTOWN CENTER R-908'},
{'value':'909', 'title': '909-BAYSHORE MALL R-909'},
{'value':'910', 'title': '910-GREECERIDGE CENTER R-910'},
{'value':'911', 'title': '911-EDEN PRAIRIE CENTER R-911'},
{'value':'915', 'title': '915-ASPEN GROVE R-915'},
{'value':'917', 'title': '917-SHOPS AT OLD MILL R917'},
{'value':'918', 'title': '918-LIME RIDGE MALL R-918'},
{'value':'919', 'title': '919-PASEO COLORADO R919'},
{'value':'920', 'title': '920-THE MALL @ ROBINSON R920'},
{'value':'923', 'title': '923-CHANDLER FASHION CTR R923'},
{'value':'925', 'title': '925-JEFFERSON POINTE R925'},
{'value':'926', 'title': '926-THE SUMMIT R926'},
{'value':'927', 'title': '927-SUPERSTITION SPRINGS R927'},
{'value':'928', 'title': '928-STREETS AT SOUTHPOINT 928'},
{'value':'931', 'title': '931-VILLAGE AT ROCHESTER'},
{'value':'933', 'title': '933-SHORT PUMP R 933'},
{'value':'934', 'title': '934-EVERGREEN WALK R-934'},
{'value':'935', 'title': '935-SHOPS AT BRIARGATE R-935'},
{'value':'936', 'title': '936-MARKET MALL (R936)'},
{'value':'938', 'title': '938-SHOPS @ CENTERRA R938'},
{'value':'939', 'title': '939-CROCKER PARK R-939'},
{'value':'940', 'title': '940-DOS LAGOS CENTER R940'},
{'value':'942', 'title': '942-FIREWHEEL R942'},
{'value':'943', 'title': '943-NORTHLAKE R943'},
{'value':'945', 'title': '945-WOODGROVE (R945)'},
{'value':'946', 'title': '946-MAIN ST @ SOUTHLANDS R946'},
{'value':'947', 'title': '947-AVENUE @ EAST COBB (R947)'},
{'value':'948', 'title': '948-SHOPPES @ GRAND PRAIRIE'},
{'value':'949', 'title': '949-TOWN SQUARE R949'},
{'value':'950', 'title': '950-CLAY TERRACE R950'},
{'value':'951', 'title': '951-THE AVENUE COLLIERVILLE'},
{'value':'952', 'title': '952-SIMI VALLEY TOWN CENTER'},
{'value':'953', 'title': '953-WOODBURY LAKES R953'},
{'value':'954', 'title': '954-UPPER CANADA MALL R954'},
{'value':'955', 'title': '955-VICTORIA GARDENS R955'},
{'value':'956', 'title': '956-NORTH EAST MALL R956'},
{'value':'959', 'title': '959-TEMP ACCUM-LIQ MS N-HOME'},
{'value':'960', 'title': '960-BEACHWOOD PLACE'},
{'value':'961', 'title': '961-SAN FRANCISCO CENTER R961'},
{'value':'962', 'title': '962-HAYWOOD MALL R962'},
{'value':'965', 'title': '965-WHSE SALE - COLUMBUS'},
{'value':'966', 'title': '966-SHOPPES AT MONTAGE R966'},
{'value':'968', 'title': '968-TOPANGA PLAZA R968'},
{'value':'969', 'title': '969-DEL AMO FASHION CTR R969'},
{'value':'970', 'title': '970-METROPOLITAN R970'},
{'value':'971', 'title': '971-PEARLAND TOWN CENTER R971'},
{'value':'972', 'title': '972-MALL @ PARTRIDGE CRK R972'},
{'value':'974', 'title': '974-CRESTVIEW HILLS R974'},
{'value':'975', 'title': '975-AVENUE @ WEST COBB R975'},
{'value':'976', 'title': '976-NORTH PARK CENTER R976'},
{'value':'977', 'title': '977-MAYFAIRE TOWN CENTER R977'},
{'value':'978', 'title': '978-NORTHFIELD @ STAPETON'},
{'value':'979', 'title': '979-TWENTY-NINTH STREET R979'},
{'value':'980', 'title': '980-BURR RIDGE R980'},
{'value':'982', 'title': '982-HILL COUNTRY GALLERIA'},
{'value':'983', 'title': '983-ZONE PRICING USOUT'},
{'value':'984', 'title': '984-WATTERS CREEK@ MONTGOMERY'},
{'value':'985', 'title': '985-ABQ UPTOWN R985'},
{'value':'986', 'title': '986-HIGHLAND VILLAGE R986'},
{'value':'987', 'title': '987-SAN TAN VILLAGE R987'},
{'value':'988', 'title': '988-SHOPPE @ SUSQUEHANNA R988'},
{'value':'989', 'title': '989-STREETS OF CHESTER R989'},
{'value':'990', 'title': '990-SQUARE ONE SHOPPING CTR'},
{'value':'991', 'title': '991-TORONTO EATON CTR R991'},
{'value':'992', 'title': '992-KING OF PRUSSIA R992'},
{'value':'993', 'title': '993-QUINTE MALL R993'},
{'value':'994', 'title': '994-ORCHARD TOWN CENTER R994'},
{'value':'995', 'title': '995-VILLAGE @ STONE OAK R995'},
{'value':'996', 'title': '996-LA CENTERRA @ CINCO RANCH'},
{'value':'997', 'title': '997-BAYSHORE TOWN CENTER R997'},
{'value':'998', 'title': '998-SMITH-HAVEN R998'},
{'value':'999', 'title': '999-THE GREENE R999'}],
     "valueSources":[
        "value"
 ]
      },
      "Product": {
      "type": 'treemultiselect',
      'valueSources': ['value'],
      "fieldSettings": {
          "treeExpandAll": False,
          "listValues":
              [{"title": "Equipment/Accessories", "value": "4", "children": [{"title": "Gift/Gadgets", "value": "4-3", "children": [{"title": "Gift/Gadgets", "value": "4-3-6", "children": [{"title": "Gift/Gadgets", "value": "4-3-6-22", "children": [{"title": "Lighting", "value": "4-3-6-22-104"}, {"title": "Other", "value": "4-3-6-22-90"}, {"title": "Tools/Gadgets", "value": "4-3-6-22-84"}, {"title": "Drink/Utensils", "value": "4-3-6-22-38"}, {"title": "Seasonal", "value": "4-3-6-22-72"}, {"title": "Umbrellas", "value": "4-3-6-22-110"}, {"title": "Sunglasses", "value": "4-3-6-22-83"}]}]}]}, {"title": "Gear", "value": "4-4", "children": [{"title": "Tents/Sleeping Bags", "value": "4-4-8", "children": [{"title": "Tents/Sleeping Bags", "value": "4-4-8-23", "children": [{"title": "Synthetic Sleeping Bags", "value": "4-4-8-23-43"}, {"title": "Down Sleeping Bags", "value": "4-4-8-23-101"}, {"title": "Expedition Tents", "value": "4-4-8-23-91"}, {"title": "Accessories", "value": "4-4-8-23-76"}, {"title": "Family Camping Tents", "value": "4-4-8-23-103"}, {"title": "Backpacking Tents", "value": "4-4-8-23-42"}]}]}, {"title": "Packs/Luggage", "value": "4-4-7", "children": [{"title": "Packs/Luggage", "value": "4-4-7-63", "children": [{"title": "Accessories", "value": "4-4-7-63-78"}, {"title": "Duffels/Rollers", "value": "4-4-7-63-79"}, {"title": "Technical Packs", "value": "4-4-7-63-89"}, {"title": "Daypacks", "value": "4-4-7-63-77"}]}]}]}, {"title": "Home", "value": "4-7", "children": [{"title": "Home", "value": "4-7-11", "children": [{"title": "Home", "value": "4-7-11-62", "children": [{"title": "Bedding", "value": "4-7-11-62-64"}, {"title": "Pillows", "value": "4-7-11-62-65"}, {"title": "Comforters", "value": "4-7-11-62-63"}]}]}]}, {"title": "Women's Access", "value": "4-6", "children": [{"title": "Women's Access.", "value": "4-6-10", "children": [{"title": "W Accessories", "value": "4-6-10-16", "children": [{"title": "W Scarves", "value": "4-6-10-16-50"}, {"title": "W Hats", "value": "4-6-10-16-48"}, {"title": "W Socks", "value": "4-6-10-16-55"}, {"title": "W Belts", "value": "4-6-10-16-51"}, {"title": "W Gloves", "value": "4-6-10-16-47"}]}]}]}, {"title": "Men's Access", "value": "4-5", "children": [{"title": "Men's Access.", "value": "4-5-9", "children": [{"title": "M Accessories", "value": "4-5-9-14", "children": [{"title": "M Hats", "value": "4-5-9-14-45"}, {"title": "M Socks", "value": "4-5-9-14-54"}, {"title": "M Gloves", "value": "4-5-9-14-46"}, {"title": "M Belts", "value": "4-5-9-14-44"}, {"title": "M Scarves", "value": "4-5-9-14-49"}]}]}]}]}, {"title": "Sportswear", "value": "1", "children": [{"title": "Men's Sportswear", "value": "1-1", "children": [{"title": "Tops", "value": "1-1-1", "children": [{"title": "Wovens", "value": "1-1-1-34", "children": [{"title": "S/S", "value": "1-1-1-34-141"}, {"title": "L/S", "value": "1-1-1-34-116"}, {"title": "Jacket", "value": "1-1-1-34-87"}]}, {"title": "Knits", "value": "1-1-1-33", "children": [{"title": "L/S", "value": "1-1-1-33-115"}, {"title": "S/S", "value": "1-1-1-33-140"}]}, {"title": "Fleece", "value": "1-1-1-29", "children": [{"title": "Pullover", "value": "1-1-1-29-32"}, {"title": "Jacket", "value": "1-1-1-29-82"}, {"title": "Vest", "value": "1-1-1-29-26"}]}, {"title": "Sweaters", "value": "1-1-1-4", "children": [{"title": "Pullover", "value": "1-1-1-4-30"}, {"title": "Cardigan", "value": "1-1-1-4-7"}]}]}, {"title": "Bottoms", "value": "1-1-2", "children": [{"title": "Wovens", "value": "1-1-2-3", "children": [{"title": "Pants", "value": "1-1-2-3-15"}, {"title": "Shorts", "value": "1-1-2-3-16"}]}, {"title": "Knits", "value": "1-1-2-66", "children": [{"title": "Pants", "value": "1-1-2-66-59"}, {"title": "Shorts", "value": "1-1-2-66-21"}]}]}]}, {"title": "Women's Sportswear", "value": "1-2", "children": [{"title": "Tops", "value": "1-2-13", "children": [{"title": "Fleece", "value": "1-2-13-31", "children": [{"title": "Pullover", "value": "1-2-13-31-37"}, {"title": "Jacket", "value": "1-2-13-31-113"}, {"title": "Vest", "value": "1-2-13-31-40"}]}, {"title": "Sweaters", "value": "1-2-13-10", "children": [{"title": "Pullover", "value": "1-2-13-10-31"}, {"title": "Cardigan", "value": "1-2-13-10-6"}]}, {"title": "Knits", "value": "1-2-13-9", "children": [{"title": "S/S", "value": "1-2-13-9-139"}, {"title": "S/L", "value": "1-2-13-9-9"}, {"title": "L/S", "value": "1-2-13-9-117"}, {"title": "3/4", "value": "1-2-13-9-11"}]}, {"title": "Wovens", "value": "1-2-13-8", "children": [{"title": "Jacket", "value": "1-2-13-8-114"}, {"title": "S/S", "value": "1-2-13-8-13"}, {"title": "3/4", "value": "1-2-13-8-12"}, {"title": "S/L", "value": "1-2-13-8-8"}, {"title": "L/S", "value": "1-2-13-8-14"}]}]}, {"title": "Bottoms", "value": "1-2-14", "children": [{"title": "Knits", "value": "1-2-14-59", "children": [{"title": "Pants", "value": "1-2-14-59-192"}, {"title": "Capri", "value": "1-2-14-59-19"}, {"title": "Shorts", "value": "1-2-14-59-20"}, {"title": "Skirt", "value": "1-2-14-59-34"}]}, {"title": "Wovens", "value": "1-2-14-11", "children": [{"title": "Pants", "value": "1-2-14-11-193"}, {"title": "Skirt", "value": "1-2-14-11-33"}, {"title": "Shorts", "value": "1-2-14-11-17"}, {"title": "Capri", "value": "1-2-14-11-18"}]}]}, {"title": "W Dresses", "value": "1-2-3", "children": [{"title": "W Dresses", "value": "1-2-3-17", "children": [{"title": "Short", "value": "1-2-3-17-35"}, {"title": "Long", "value": "1-2-3-17-36"}]}]}]}]}, {"title": "Footwear", "value": "3", "children": [{"title": "Women's Footwear", "value": "3-12", "children": [{"title": "Perf Outdoor", "value": "3-12-19", "children": [{"title": "Perf Outdoor", "value": "3-12-19-53", "children": [{"title": "Cold Weather", "value": "3-12-19-53-57"}, {"title": "Hiking", "value": "3-12-19-53-75"}, {"title": "Trail and Multi-Sport", "value": "3-12-19-53-86"}, {"title": "Water", "value": "3-12-19-53-71"}]}]}, {"title": "Lifestyle", "value": "3-12-20", "children": [{"title": "Lifestyle", "value": "3-12-20-20", "children": [{"title": "Casual", "value": "3-12-20-20-62"}, {"title": "Slippers", "value": "3-12-20-20-68"}, {"title": "Dress Casual", "value": "3-12-20-20-60"}]}]}]}, {"title": "Men's Footwear", "value": "3-11", "children": [{"title": "Lifestyle", "value": "3-11-5", "children": [{"title": "Lifestyle", "value": "3-11-5-19", "children": [{"title": "Slippers", "value": "3-11-5-19-61"}, {"title": "Dress Casual", "value": "3-11-5-19-58"}, {"title": "Casual", "value": "3-11-5-19-69"}]}]}, {"title": "Perf Outdoor", "value": "3-11-4", "children": [{"title": "Perf Outdoor", "value": "3-11-4-52", "children": [{"title": "Hiking", "value": "3-11-4-52-74"}, {"title": "Cold Weather", "value": "3-11-4-52-56"}, {"title": "Trail and Multi-Sport", "value": "3-11-4-52-85"}, {"title": "Water", "value": "3-11-4-52-73"}]}]}]}]}, {"title": "Outerwear", "value": "2", "children": [{"title": "Women's Outerwear", "value": "2-10", "children": [{"title": "Tops", "value": "2-10-16", "children": [{"title": "W Non-WP Tops", "value": "2-10-16-26", "children": [{"title": "Parka/Trench", "value": "2-10-16-26-133"}, {"title": "Vest", "value": "2-10-16-26-23"}, {"title": "Jacket", "value": "2-10-16-26-97"}]}, {"title": "W Non-WP Insul Tops", "value": "2-10-16-28", "children": [{"title": "Parka/Trench", "value": "2-10-16-28-135"}, {"title": "Vest", "value": "2-10-16-28-24"}, {"title": "Jacket", "value": "2-10-16-28-96"}]}, {"title": "W WP Shells", "value": "2-10-16-6", "children": [{"title": "Parka/Trench", "value": "2-10-16-6-131"}, {"title": "Jacket", "value": "2-10-16-6-70"}]}, {"title": "W Insul WP Shells", "value": "2-10-16-89", "children": [{"title": "Jacket", "value": "2-10-16-89-88"}, {"title": "Parka/Trench", "value": "2-10-16-89-138"}, {"title": "Conv/3-in-1", "value": "2-10-16-89-67"}]}, {"title": "Fleece", "value": "2-10-16-56", "children": [{"title": "Jacket", "value": "2-10-16-56-100"}, {"title": "Vest", "value": "2-10-16-56-22"}, {"title": "Parka/Trench", "value": "2-10-16-56-136"}]}]}, {"title": "Bottoms", "value": "2-10-18", "children": [{"title": "Bottoms", "value": "2-10-18-39", "children": [{"title": "Bottoms", "value": "2-10-18-39-29"}]}]}]}, {"title": "Men's Outerwear", "value": "2-9", "children": [{"title": "Tops", "value": "2-9-15", "children": [{"title": "M Insul WP Shells", "value": "2-9-15-88", "children": [{"title": "Conv/3-in-1", "value": "2-9-15-88-66"}, {"title": "Parka/Trench", "value": "2-9-15-88-194"}, {"title": "Jacket", "value": "2-9-15-88-41"}]}, {"title": "M Non-WP Tops", "value": "2-9-15-25", "children": [{"title": "Jacket", "value": "2-9-15-25-53"}, {"title": "Parka/Trench", "value": "2-9-15-25-132"}, {"title": "Vest", "value": "2-9-15-25-1"}]}, {"title": "M WP Shells", "value": "2-9-15-1", "children": [{"title": "Parka/Trench", "value": "2-9-15-1-3"}, {"title": "Jacket", "value": "2-9-15-1-2"}]}, {"title": "M Non-WP Insul Tops", "value": "2-9-15-27", "children": [{"title": "Jacket", "value": "2-9-15-27-52"}, {"title": "Parka/Trench", "value": "2-9-15-27-195"}, {"title": "Vest", "value": "2-9-15-27-5"}]}, {"title": "Fleece", "value": "2-9-15-51", "children": [{"title": "Jacket", "value": "2-9-15-51-81"}, {"title": "Vest", "value": "2-9-15-51-27"}]}]}, {"title": "Bottoms", "value": "2-9-17", "children": [{"title": "Bottoms", "value": "2-9-17-38", "children": [{"title": "Bottoms", "value": "2-9-17-38-28"}]}]}]}]}, {"title": "Kids", "value": "5", "children": [{"title": "Kids", "value": "5-8", "children": [{"title": "Kids", "value": "5-8-12", "children": [{"title": "Kids", "value": "5-8-12-87", "children": [{"title": "Kids", "value": "5-8-12-87-25"}]}]}]}]}]

      }
  }
   }
}


d['universe']['weather'] = {
   "label":"Weather",
   "type":"!group",
   "subfields":{

      "maximum_temperature_apparent":{
      "label": "Max Temperature Feels Like (F)",
         "type":"number",
         "valueSources":[
            "value"
         ]
      },
      "maximum_temperature_apparent_mean":{
      "label": "Max Temperature (Feels Like) Anomoly (F)",
         "type":"number",
         "valueSources":[
            "value"
         ]
      },
      "maximum_temperature":{
      "label": "Max Temperature (F)",
         "type":"number",
         "valueSources":[
            "value"
         ]
      },
      "maximum_temperature_mean":{
      "label": "Max Temperature Anomoly (F)",
         "type":"number",
         "valueSources":[
            "value"
         ]
      },
      "minimum_temperature_apparent":{
      "label": "Min Temperature (Feels Like) (F)",
         "type":"number",
         "valueSources":[
            "value"
         ]
      },
      "minimum_temperature_apparent_mean":{
      "label": "Min Temperature (Feels Like) Anomoly (F)",
         "type":"number",
         "valueSources":[
            "value"
         ]
      },
      "minimum_temperature":{
      "label": "Min Temperature (F)",
         "type":"number",
         "valueSources":[
            "value"
         ]
      },
      "minimum_temperature_mean":{
      "label": "Min Temperature Anomoly (F)",
         "type":"number",
         "valueSources":[
            "value"
         ]
      },
      "total_precipitation":{
      "label": "Total Precipitation",
         "type":"number",
         "valueSources":[
            "value"
         ]
      },
      "total_precipitation_mean":{
      "label": "Total Precipitation Anomoly",
         "type":"number",
         "valueSources":[
            "value"
         ]
      },
      "precip_rain":{
      "label": "Rain",
         "type":"number",
         "valueSources":[
            "value"
         ]
      },
      "precip_rain_mean":{
      "label": "Rain Anomoly",
         "type":"number",
         "valueSources":[
            "value"
         ]
      },
      "precip_snow":{
      "label": "Snow",
         "type":"number",
         "valueSources":[
            "value"
         ]
      },
      "precip_snow_mean":{
      "label": "Snow Anomoly",
         "type":"number",
         "valueSources":[
            "value"
         ]
      },
      "sunshine_duration":{
      "label": "Hours of Sunshine",
         "type":"number",
         "valueSources":[
            "value"
         ]
      },
      "sunshine_duration_mean":{
      "label": "Hours of Sunshine Anomoly",
         "type":"number",
         "valueSources":[
            "value"
         ]
      },
      "wind_speed_gust":{
      "label": "Wind (mph)",
         "type":"number",
         "valueSources":[
            "value"
         ]
      },
      "wind_speed_gust_mean":{
      "label": "Wind Anomoly (mph)",
         "type":"number",
         "valueSources":[
            "value"
         ]
      },

      "Time Period":{
      "label": 'Time Period (Absolute)',
         "type":"date",
         "fieldSettings":{
            "dateFormat":"MM-DD-YYYY"
         },
         "valueSources":[
            "value"
         ],
           "widgets": {
               "date": {
                       "operators": ['between'],
                       "widgetProps": {
                           "hideOperator": True,
                           "operatorInlineLabel": "between",
                           }
                       },
                   }
      },
        "Days Ahead":{
              "label": 'Time Period (Relative)',
              "type": 'number',
              "valueSources": ['value', 'field'],
              "fieldSettings": {
                  "min": -1500,
                  "max": 10,
                  "step": 1,
                  "marks": {
                      0: "0",
                      365: "365"
                  }
              },
              "widgets": {
                  "number": {
                          "operators": ['between'],
                          "widgetProps": {
                              "hideOperator": True,
                              "operatorInlineLabel": "between",
                              }
                          },
                      }
          },
      "Value":{
         "type":"number",
         "valueSources":[
            "value"
         ]
      },

   }
}

d['universe']['gender'] = {
    "label":"Gender",
    "type":"select",
    "listValues":[{"value": 'male', "title": "Male"}
    ,{"value": 'female', "title": "Female"}
    ,{"value": 'unknown', "title": "Unknown"}],
    "valueSources":[
    "value"
    ]
}

d['universe']['zip_country'] = {
    "label":"Country",
    "type":"select",
    "listValues":[{"value": 'US', "title": "US"}
    ,{"value": 'CA', "title": "CA"}],
    "valueSources":[
    "value"
    ]
}

d['universe']['age'] = {
    "label":"Age",
    "type":"select",
    "listValues":['10-20', '21-30', '31-40', '41-50', '51-60', '61-70', '71+', 'Unknown'],
    "valueSources":[
    "value"
    ]
}

d['universe']['employee_flag'] = {
    "label":"Employee",
    "type":"select",
    "listValues":[{"value": 'Y', "title": "Yes"}
    ,{"value": 'N', "title": "No"}],
    "valueSources":[
    "value"
    ]
}

d['universe']['loyalty_tier'] = {
    "label":"Loyalty",
    "type":"select",
    "listValues":['Green', 'Bronze', 'Silver', 'Gold', 'Non-AR'],
    "valueSources":[
    "value"
    ]
}

d['universe']['audiences'] = {
    "label":"Audiences",
       "type":"!group",
       "subfields":{


          "Audience Customers":{
             "type":"select",
             "listValues":[{"value": 'audience_1', "title": "audience_1"}
             ,{"value": 'audience_2', "title": "audience_2"}
             ,{"value": 'audience_3', "title": "audience_3"}],
             "valueSources":[
                "value"
             ]
          },

          "Test / Control":{
             "type":"multiselect",
               "widgets": {
                 "multiselect": {
                             "operators": ['select_any_in'],
                     "widgetProps": {
                         "hideOperator": True,
                         "operatorInlineLabel": "include",
                     }
                 }
                 },
             "listValues":[{"value": 'test', "title": "Test"}
             ,{"value": 'holdout', "title": "Control"}],
             "valueSources":[
                "value"
             ]
          }
         }

}


d['universe']['cordial'] = {
    "label":"Cordial",
       "type":"!group",
       "subfields":{
          "frequency_string":{
             "type":"multiselect",
               "widgets": {
                 "multiselect": {
                             "operators": ['select_any_in', 'is_empty', 'is_not_empty'],
                 }
                 },
             "listValues":[{"value": 'daily', "title": "daily"}
             ,{"value": 'weekly', "title": "weekly"}, {"value": 'monthly', "title": "monthly"}, {"value": '', "title": "blank"}],
             "valueSources":[
                "value"
             ]
          },
          "loyalty_tier_name":{
             "type":"multiselect",
               "widgets": {
                 "multiselect": {
                             "operators": ['select_any_in', 'is_empty', 'is_not_empty'],
                 }
                 },
             "listValues":[{"value": 'Gold', "title": "Gold"}
             ,{"value": 'Bronze', "title": "Bronze"}, {"value": 'Silver', "title": "Silver"}, {"value": 'Green', "title": "Green"}, {"value": 'bronze', "title": "bronze"}, {"value": '', "title": "blank"}],
             "valueSources":[
                "value"
             ]
          },
          "channels_email_subscribestatus":{
             "type":"multiselect",
               "widgets": {
                 "multiselect": {
                             "operators": ['select_any_in', 'is_empty', 'is_not_empty'],
                 }
                 },
             "listValues":[{"value": 'subscribed', "title": "subscribed"}
             ,{"value": 'unsubscribed', "title": "unsubscribed"}, {"value": 'none', "title": "none"}, {"value": '', "title": "blank"}],
             "valueSources":[
                "value"
             ]
          },
          "channels_sms_subscribestatus":{
             "type":"multiselect",
               "widgets": {
                 "multiselect": {
                             "operators": ['select_any_in', 'is_empty', 'is_not_empty'],
                 }
                 },
             "listValues":[{"value": 'subscribed', "title": "subscribed"}
             ,{"value": 'unsubscribed', "title": "unsubscribed"}, {"value": 'none', "title": "none"}, {"value": '', "title": "blank"}],
             "valueSources":[
                "value"
             ]
          },
          "in_cordial":{
             "type":"select",
               "widgets": {
                 "multiselect": {
                             "operators": ['equal'],
                 }
                 },
             "listValues":[{"value": 'yes', "title": "yes"}, {"value": 'no', "title": "no"}],
             "valueSources":[
                "value"
             ]
          },
          "loyalty_balance":{
             "type":"number",
             "valueSources":[
                "value"
             ]
          },
          "loyalty_lifetime_balance":{
             "type":"number",
             "valueSources":[
                "value"
             ]
          },
          "spend_to_tier":{
             "type":"number",
             "valueSources":[
                "value"
             ]
          }
         }

}

d['ml']['transact_probability'] = {
   "label":"High Transaction Probability",
   "type":"!group",
   "subfields":{
      "Channel":{
         "type":"multiselect",
           "widgets": {
             "multiselect": {
                         "operators": ['select_any_in'],
                 "widgetProps": {
                     "hideOperator": True,
                     "operatorInlineLabel": "include",
                 }
             }
             },
         "listValues":[{"value": 'Retail', "title": "FP Store"}
         ,{"value": 'Direct', "title": "Direct"}
         ,{"value": 'Outlet', "title": "Outlet"}],
         "valueSources":[
            "value"
         ]
      },
      "Days Ahead":{
            "label": 'Days Ahead (Relative)',
            "type": 'number',
            "valueSources": ['value', 'field'],
            "fieldSettings": {
                "min": 0,
                "max": 200,
                "step": 7,
                "marks": {
                    0: "0",
                    365: "365"
                }
            },
            "widgets": {
                "number": {
                        "operators": ['between'],
                        "widgetProps": {
                            "hideOperator": True,
                            "operatorInlineLabel": "between",
                            }
                        },
                    }
        },
        "Importance":{
          "type":"select",
          "widgets": {
            "select": {
                        "operators": ['equal'],
                "widgetProps": {
                    "hideOperator": True,
                    "operatorInlineLabel": "is",
                }
            },
        },
         "listValues":[{"value": "1", "title": "1 (Lowest)"}
         ,{"value": "2", "title": "2"}
         ,{"value": "3", "title": "3 (Default)"}
         ,{"value": "4", "title": "4"}
         ,{"value": "5", "title": "5 (Highest)"}],
           "valueSources":[
              "value"
           ],
           "defaultValue":3
        },

            "Product": {
            "type": 'treemultiselect',
            'valueSources': ['value'],
            "fieldSettings": {
                "treeExpandAll": False,
                "listValues":
                    [{"title": "Equipment/Accessories", "value": "4", "children": [{"title": "Gift/Gadgets", "value": "4-3", "children": [{"title": "Gift/Gadgets", "value": "4-3-6", "children": [{"title": "Gift/Gadgets", "value": "4-3-6-22", "children": [{"title": "Lighting", "value": "4-3-6-22-104"}, {"title": "Other", "value": "4-3-6-22-90"}, {"title": "Tools/Gadgets", "value": "4-3-6-22-84"}, {"title": "Drink/Utensils", "value": "4-3-6-22-38"}, {"title": "Seasonal", "value": "4-3-6-22-72"}, {"title": "Umbrellas", "value": "4-3-6-22-110"}, {"title": "Sunglasses", "value": "4-3-6-22-83"}]}]}]}, {"title": "Gear", "value": "4-4", "children": [{"title": "Tents/Sleeping Bags", "value": "4-4-8", "children": [{"title": "Tents/Sleeping Bags", "value": "4-4-8-23", "children": [{"title": "Synthetic Sleeping Bags", "value": "4-4-8-23-43"}, {"title": "Down Sleeping Bags", "value": "4-4-8-23-101"}, {"title": "Expedition Tents", "value": "4-4-8-23-91"}, {"title": "Accessories", "value": "4-4-8-23-76"}, {"title": "Family Camping Tents", "value": "4-4-8-23-103"}, {"title": "Backpacking Tents", "value": "4-4-8-23-42"}]}]}, {"title": "Packs/Luggage", "value": "4-4-7", "children": [{"title": "Packs/Luggage", "value": "4-4-7-63", "children": [{"title": "Accessories", "value": "4-4-7-63-78"}, {"title": "Duffels/Rollers", "value": "4-4-7-63-79"}, {"title": "Technical Packs", "value": "4-4-7-63-89"}, {"title": "Daypacks", "value": "4-4-7-63-77"}]}]}]}, {"title": "Home", "value": "4-7", "children": [{"title": "Home", "value": "4-7-11", "children": [{"title": "Home", "value": "4-7-11-62", "children": [{"title": "Bedding", "value": "4-7-11-62-64"}, {"title": "Pillows", "value": "4-7-11-62-65"}, {"title": "Comforters", "value": "4-7-11-62-63"}]}]}]}, {"title": "Women's Access", "value": "4-6", "children": [{"title": "Women's Access.", "value": "4-6-10", "children": [{"title": "W Accessories", "value": "4-6-10-16", "children": [{"title": "W Scarves", "value": "4-6-10-16-50"}, {"title": "W Hats", "value": "4-6-10-16-48"}, {"title": "W Socks", "value": "4-6-10-16-55"}, {"title": "W Belts", "value": "4-6-10-16-51"}, {"title": "W Gloves", "value": "4-6-10-16-47"}]}]}]}, {"title": "Men's Access", "value": "4-5", "children": [{"title": "Men's Access.", "value": "4-5-9", "children": [{"title": "M Accessories", "value": "4-5-9-14", "children": [{"title": "M Hats", "value": "4-5-9-14-45"}, {"title": "M Socks", "value": "4-5-9-14-54"}, {"title": "M Gloves", "value": "4-5-9-14-46"}, {"title": "M Belts", "value": "4-5-9-14-44"}, {"title": "M Scarves", "value": "4-5-9-14-49"}]}]}]}]}, {"title": "Sportswear", "value": "1", "children": [{"title": "Men's Sportswear", "value": "1-1", "children": [{"title": "Tops", "value": "1-1-1", "children": [{"title": "Wovens", "value": "1-1-1-34", "children": [{"title": "S/S", "value": "1-1-1-34-141"}, {"title": "L/S", "value": "1-1-1-34-116"}, {"title": "Jacket", "value": "1-1-1-34-87"}]}, {"title": "Knits", "value": "1-1-1-33", "children": [{"title": "L/S", "value": "1-1-1-33-115"}, {"title": "S/S", "value": "1-1-1-33-140"}]}, {"title": "Fleece", "value": "1-1-1-29", "children": [{"title": "Pullover", "value": "1-1-1-29-32"}, {"title": "Jacket", "value": "1-1-1-29-82"}, {"title": "Vest", "value": "1-1-1-29-26"}]}, {"title": "Sweaters", "value": "1-1-1-4", "children": [{"title": "Pullover", "value": "1-1-1-4-30"}, {"title": "Cardigan", "value": "1-1-1-4-7"}]}]}, {"title": "Bottoms", "value": "1-1-2", "children": [{"title": "Wovens", "value": "1-1-2-3", "children": [{"title": "Pants", "value": "1-1-2-3-15"}, {"title": "Shorts", "value": "1-1-2-3-16"}]}, {"title": "Knits", "value": "1-1-2-66", "children": [{"title": "Pants", "value": "1-1-2-66-59"}, {"title": "Shorts", "value": "1-1-2-66-21"}]}]}]}, {"title": "Women's Sportswear", "value": "1-2", "children": [{"title": "Tops", "value": "1-2-13", "children": [{"title": "Fleece", "value": "1-2-13-31", "children": [{"title": "Pullover", "value": "1-2-13-31-37"}, {"title": "Jacket", "value": "1-2-13-31-113"}, {"title": "Vest", "value": "1-2-13-31-40"}]}, {"title": "Sweaters", "value": "1-2-13-10", "children": [{"title": "Pullover", "value": "1-2-13-10-31"}, {"title": "Cardigan", "value": "1-2-13-10-6"}]}, {"title": "Knits", "value": "1-2-13-9", "children": [{"title": "S/S", "value": "1-2-13-9-139"}, {"title": "S/L", "value": "1-2-13-9-9"}, {"title": "L/S", "value": "1-2-13-9-117"}, {"title": "3/4", "value": "1-2-13-9-11"}]}, {"title": "Wovens", "value": "1-2-13-8", "children": [{"title": "Jacket", "value": "1-2-13-8-114"}, {"title": "S/S", "value": "1-2-13-8-13"}, {"title": "3/4", "value": "1-2-13-8-12"}, {"title": "S/L", "value": "1-2-13-8-8"}, {"title": "L/S", "value": "1-2-13-8-14"}]}]}, {"title": "Bottoms", "value": "1-2-14", "children": [{"title": "Knits", "value": "1-2-14-59", "children": [{"title": "Pants", "value": "1-2-14-59-192"}, {"title": "Capri", "value": "1-2-14-59-19"}, {"title": "Shorts", "value": "1-2-14-59-20"}, {"title": "Skirt", "value": "1-2-14-59-34"}]}, {"title": "Wovens", "value": "1-2-14-11", "children": [{"title": "Pants", "value": "1-2-14-11-193"}, {"title": "Skirt", "value": "1-2-14-11-33"}, {"title": "Shorts", "value": "1-2-14-11-17"}, {"title": "Capri", "value": "1-2-14-11-18"}]}]}, {"title": "W Dresses", "value": "1-2-3", "children": [{"title": "W Dresses", "value": "1-2-3-17", "children": [{"title": "Short", "value": "1-2-3-17-35"}, {"title": "Long", "value": "1-2-3-17-36"}]}]}]}]}, {"title": "Footwear", "value": "3", "children": [{"title": "Women's Footwear", "value": "3-12", "children": [{"title": "Perf Outdoor", "value": "3-12-19", "children": [{"title": "Perf Outdoor", "value": "3-12-19-53", "children": [{"title": "Cold Weather", "value": "3-12-19-53-57"}, {"title": "Hiking", "value": "3-12-19-53-75"}, {"title": "Trail and Multi-Sport", "value": "3-12-19-53-86"}, {"title": "Water", "value": "3-12-19-53-71"}]}]}, {"title": "Lifestyle", "value": "3-12-20", "children": [{"title": "Lifestyle", "value": "3-12-20-20", "children": [{"title": "Casual", "value": "3-12-20-20-62"}, {"title": "Slippers", "value": "3-12-20-20-68"}, {"title": "Dress Casual", "value": "3-12-20-20-60"}]}]}]}, {"title": "Men's Footwear", "value": "3-11", "children": [{"title": "Lifestyle", "value": "3-11-5", "children": [{"title": "Lifestyle", "value": "3-11-5-19", "children": [{"title": "Slippers", "value": "3-11-5-19-61"}, {"title": "Dress Casual", "value": "3-11-5-19-58"}, {"title": "Casual", "value": "3-11-5-19-69"}]}]}, {"title": "Perf Outdoor", "value": "3-11-4", "children": [{"title": "Perf Outdoor", "value": "3-11-4-52", "children": [{"title": "Hiking", "value": "3-11-4-52-74"}, {"title": "Cold Weather", "value": "3-11-4-52-56"}, {"title": "Trail and Multi-Sport", "value": "3-11-4-52-85"}, {"title": "Water", "value": "3-11-4-52-73"}]}]}]}]}, {"title": "Outerwear", "value": "2", "children": [{"title": "Women's Outerwear", "value": "2-10", "children": [{"title": "Tops", "value": "2-10-16", "children": [{"title": "W Non-WP Tops", "value": "2-10-16-26", "children": [{"title": "Parka/Trench", "value": "2-10-16-26-133"}, {"title": "Vest", "value": "2-10-16-26-23"}, {"title": "Jacket", "value": "2-10-16-26-97"}]}, {"title": "W Non-WP Insul Tops", "value": "2-10-16-28", "children": [{"title": "Parka/Trench", "value": "2-10-16-28-135"}, {"title": "Vest", "value": "2-10-16-28-24"}, {"title": "Jacket", "value": "2-10-16-28-96"}]}, {"title": "W WP Shells", "value": "2-10-16-6", "children": [{"title": "Parka/Trench", "value": "2-10-16-6-131"}, {"title": "Jacket", "value": "2-10-16-6-70"}]}, {"title": "W Insul WP Shells", "value": "2-10-16-89", "children": [{"title": "Jacket", "value": "2-10-16-89-88"}, {"title": "Parka/Trench", "value": "2-10-16-89-138"}, {"title": "Conv/3-in-1", "value": "2-10-16-89-67"}]}, {"title": "Fleece", "value": "2-10-16-56", "children": [{"title": "Jacket", "value": "2-10-16-56-100"}, {"title": "Vest", "value": "2-10-16-56-22"}, {"title": "Parka/Trench", "value": "2-10-16-56-136"}]}]}, {"title": "Bottoms", "value": "2-10-18", "children": [{"title": "Bottoms", "value": "2-10-18-39", "children": [{"title": "Bottoms", "value": "2-10-18-39-29"}]}]}]}, {"title": "Men's Outerwear", "value": "2-9", "children": [{"title": "Tops", "value": "2-9-15", "children": [{"title": "M Insul WP Shells", "value": "2-9-15-88", "children": [{"title": "Conv/3-in-1", "value": "2-9-15-88-66"}, {"title": "Parka/Trench", "value": "2-9-15-88-194"}, {"title": "Jacket", "value": "2-9-15-88-41"}]}, {"title": "M Non-WP Tops", "value": "2-9-15-25", "children": [{"title": "Jacket", "value": "2-9-15-25-53"}, {"title": "Parka/Trench", "value": "2-9-15-25-132"}, {"title": "Vest", "value": "2-9-15-25-1"}]}, {"title": "M WP Shells", "value": "2-9-15-1", "children": [{"title": "Parka/Trench", "value": "2-9-15-1-3"}, {"title": "Jacket", "value": "2-9-15-1-2"}]}, {"title": "M Non-WP Insul Tops", "value": "2-9-15-27", "children": [{"title": "Jacket", "value": "2-9-15-27-52"}, {"title": "Parka/Trench", "value": "2-9-15-27-195"}, {"title": "Vest", "value": "2-9-15-27-5"}]}, {"title": "Fleece", "value": "2-9-15-51", "children": [{"title": "Jacket", "value": "2-9-15-51-81"}, {"title": "Vest", "value": "2-9-15-51-27"}]}]}, {"title": "Bottoms", "value": "2-9-17", "children": [{"title": "Bottoms", "value": "2-9-17-38", "children": [{"title": "Bottoms", "value": "2-9-17-38-28"}]}]}]}]}]

            }
        },


   }
}


d['ml']['churn'] = {
"label":"Churn",
   "type":"!group",
   "subfields":{
   "Churn Risk":{
      "type":"select",
          "widgets": {
            "select": {
            "operators": ['equal'],
                "widgetProps": {
                    "hideOperator": True,
                    "operatorInlineLabel": "is",
                }
            },
        },
        "listValues":[{"value": 'high', "title": "High"}
        ,{"value": 'low', "title": "Low"}],
          "valueSources":[
             "value"
          ]
       },


          "Channel":{
             "type":"multiselect",
               "widgets": {
                 "multiselect": {
                             "operators": ['select_any_in'],
                     "widgetProps": {
                         "hideOperator": True,
                         "operatorInlineLabel": "include",
                     }
                 }
                 },
             "listValues":[{"value": 'Retail', "title": "FP Store"}
             ,{"value": 'Direct', "title": "Direct"}
             ,{"value": 'Outlet', "title": "Outlet"}],
             "valueSources":[
                "value"
             ]
          },




        "Importance":{
          "type":"select",
          "widgets": {
            "select": {
                        "operators": ['equal'],
                "widgetProps": {
                    "hideOperator": True,
                    "operatorInlineLabel": "is",
                }
            },
        },
         "listValues":[{"value": "1", "title": "1 (Lowest)"}
         ,{"value": "2", "title": "2"}
         ,{"value": "3", "title": "3 (Default)"}
         ,{"value": "4", "title": "4"}
         ,{"value": "5", "title": "5 (Highest)"}],
           "valueSources":[
              "value"
           ],
           "defaultValue": "3"
        }
   }
}


d['ml']['clv'] = {
"label":"CLV",
   "type":"!group",
   "subfields":{
   "CLV":{
      "type":"select",
          "widgets": {
            "select": {
            "operators": ['equal'],
                "widgetProps": {
                    "hideOperator": True,
                    "operatorInlineLabel": "is",
                }
            },
        },
        "listValues":[{"value": 'high', "title": "High"}
        ,{"value": 'low', "title": "Low"}],
          "valueSources":[
             "value"
          ]
       },
          "Channel":{
             "type":"multiselect",
               "widgets": {
                 "multiselect": {
                             "operators": ['select_any_in'],
                     "widgetProps": {
                         "hideOperator": True,
                         "operatorInlineLabel": "include",
                     }
                 }
                 },
             "listValues":[{"value": 'Retail', "title": "FP Store"}
             ,{"value": 'Direct', "title": "Direct"}
             ,{"value": 'Outlet', "title": "Outlet"}],
             "valueSources":[
                "value"
             ]
          },
        "Importance":{
          "type":"select",
          "widgets": {
            "select": {
                        "operators": ['equal'],
                "widgetProps": {
                    "hideOperator": True,
                    "operatorInlineLabel": "is",
                }
            },
        },
         "listValues":[{"value": "1", "title": "1 (Lowest)"}
         ,{"value": "2", "title": "2"}
         ,{"value": "3", "title": "3 (Default)"}
         ,{"value": "4", "title": "4"}
         ,{"value": "5", "title": "5 (Highest)"}],
           "valueSources":[
              "value"
           ],
           "defaultValue":3
        }
   }
}


y = json.dumps(d)
with open("audience_query_fields.json", "w") as f:
    f.write(y)

boto3.Session().resource('s3').Bucket('wx-params').Object('audience_json/audience_query_fields.json').upload_file("audience_query_fields.json")