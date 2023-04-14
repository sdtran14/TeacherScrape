import scrapy
import logging
import requests
import json
import csv

class RmpsearchSpider(scrapy.Spider):
    name = 'rmpSearch'
    allowed_domains = ['www.ratemyprofessors.com']
    global profSectionsDict
    profSectionsDict = {}
    global profClassDict
    profClassDict = {}
    global schoolID
    schoolID = 'U2Nob29sLTEzODE='
    global fields 
    fields = ["Class",
              "Instructor",
              "SectionID",
              "Found",
              "RMP Name",
              "Avg. Rating",
              "Avg. Difficulty",
              "# of Ratings",
              "would-Take-Again-Percent",
              "url"]
    with open("feed.csv", 'r') as file:
        csvreader = csv.reader(file)
        next(csvreader)
        for row in csvreader:
            
            profSectionsDict[str(row[0])] = row[1].strip('][').split(', ')
            profClassDict[str(row[0])] = row[2].strip('][').split(', ')
    start_urls = []
    for key in profSectionsDict.keys():
        #print(key.replace(' ', '%20'))
        start_urls.append('https://www.ratemyprofessors.com/search/teachers?query='+
                          key.replace(' ', '%20') +
                          '&sid=' + schoolID
                          )
    logging.getLogger('scrapy').setLevel(logging.WARNING)
    
    with open('search.csv', 'w', newline='') as file:
        writer= csv.DictWriter(file, fieldnames = fields)
        writer.writeheader()
        
    '''
    def urlify(name):
        name = replace(name, ' ', '%20')
    '''

    def parse(self, response):
        with open('search.csv', 'a') as file:
            tempRes = []
            tempDict = {}
            
            inst = str(response.url.split
            ('https://www.ratemyprofessors.com/search/teachers?query=')[-1].split
            ('&sid=')[0].replace
            ('%20', ' '))
            
            
            tempDict["Class"] = profClassDict[inst]
            tempDict["Instructor"] = inst
            tempDict["SectionID"] = profSectionsDict[inst]
            tempDict["Found"] = "False"
            tempDict["RMP Name"] = "N/A"
            tempDict["Avg. Rating"] = "N/A"
            tempDict["Avg. Difficulty"] = "N/A"
            tempDict["# of Ratings"] = "N/A"
            tempDict["would-Take-Again-Percent"] = "N/A"
            tempDict['url'] = "N/A"
            #print(fields)
            
            writer= csv.DictWriter(file, fieldnames = fields)
            #print(tempDict)
            
            
            
            script = response.xpath('//script')[-2]
            script = script.xpath('.//text()').get()
            script = script.split(' window.__RELAY_STORE__ = ')[-1]
            script = script.split(';')[0]
            
            #print(script)
            data = json.loads(script)
            for key, value in data.items():
                #print(value)
                if 'lastName' in value:
                    
                    
                    #print(value['school']['__ref'])
                    if value['school']['__ref'] == schoolID:
                        tempDict["Found"] = "True" 
                        tempDict["RMP Name"] =  value['firstName'] + " " + value['lastName']
                        tempDict["Avg. Rating"] = value['avgRating']
                        tempDict["Avg. Difficulty"] = value['avgDifficulty']
                        tempDict["# of Ratings"] = value['numRatings']
                        tempDict["would-Take-Again-Percent"] = value['wouldTakeAgainPercent']
                        tempDict['url'] = "https://www.ratemyprofessors.com/professor/" + str(value['legacyId'])
                    
                    #print(tempDict)
                    break;
            tempRes.append(tempDict)
            writer.writerows(tempRes)
                #print('-'*15)
            #classDiv = response.xpath('//div[@id="root"]/div/div/div')[3].get()
            
            #classDiv = classDiv.xpath('.//div[@class]')
            #print(data)
        
        pass
