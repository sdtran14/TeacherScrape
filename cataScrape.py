import scrapy
import logging
import csv
#import config 

class CatascrapeSpider(scrapy.Spider):
    name = 'cataScrape'
    allowed_domains = ['classes.usc.edu']
    #ClassID = 'WRIT-150'
    global depIDDict
    depIDDict = {}
    with open('inputs.txt', 'r') as file_object:
        
        line = file_object.readline()
        #print(type(line))
        while line:
            dep, ID = line.split(' ', 1)
            #print(dep)
            
            ID = ID.split(" ", 1)[0]
            ID = ID.split('\t', 1)[0]
            
            #print(ID[:3])
            #print(codes)
            if dep not in depIDDict:
                depIDDict[dep] = []
            depIDDict[dep].append(ID)
            line = file_object.readline()
            
    #depIDDict['AMST'] = ["135"] #adds WRIT-150
    start_urls = []
    for key in depIDDict.keys():
        start_urls.append('http://classes.usc.edu/term-20233/classes/'+key)
    
    global fields
    fields = ["Instructor", "SectionID", "Class"]
    with open('feed.csv', 'w', newline='') as file:
        writer= csv.DictWriter(file, fieldnames = fields)
        writer.writeheader()
    
    logging.getLogger('scrapy').setLevel(logging.WARNING)
    def parse(self, response):
        sectionsDicts = []
        profSectionsDict = {}
        with open('feed.csv', 'a', newline='') as file:
            dep = str(response.url.split('/')[-1])
            
            profClassDict = {}
            classIDs = depIDDict[dep]
            #print(classIDs)
            for ClassID in classIDs:
                classDiv = response.xpath(f'//div[@id="{dep}-{ClassID[:3]}"]')
                #print(classDiv)
                for section in classDiv.xpath('.//tr'):
                    #print(section.xpath('.//@data-section-id').get())
                    sectionID = section.xpath('.//td[@class="section"]/text()').get()
                    if(sectionID != None):
                        
                        
                        inst = section.xpath('.//td[@class="instructor"]/text()').get()
                        if(inst == None): 
                            inst =section.xpath('.//td[@class="instructor"]/a/text()').get()
                        if str(inst) not in profSectionsDict:
                            profSectionsDict[str(inst)] = []
                        if str(inst) not in profClassDict:
                            profClassDict[str(inst)] = []
                        
                        profSectionsDict[str(inst)].append(sectionID)
                        
                        cID = f'{dep}-{ClassID}'
                        if cID not in profClassDict[str(inst)]:
                            profClassDict[str(inst)].append(cID)
                        
                   
                    #print(sectionID)
            for prof, sectionList in profSectionsDict.items():
                tempDict = {}
                tempDict['Instructor'] = prof
                tempDict['SectionID']=  sectionList
                tempDict['Class'] = profClassDict[prof]
                #print(prof)
                if prof != "None": sectionsDicts.append(tempDict)
            writer= csv.DictWriter(file, fieldnames = fields)
            writer.writerows(sectionsDicts)
        pass
