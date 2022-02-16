from multiprocessing import Pool
import requests
import argparse
import signal

class Dir_Finder():
    def __init__(self,target,file,extensions,output_file,blacklist_status_code,threads):
        self.target = target
        self.file = file
        self.extensions = extensions
        self.output_file = output_file
        self.blacklist_status_code = blacklist_status_code
        self.threads = threads
        
        self.logo()
        self.ext_list = self.create_extensions()
        self.url = self.check_url()
        self.headers = self.create_header()
        self.options_and_wordlistset()

    def logo(self):
        display = "╔═══╗───╔═══╗─────╔╗\n" 
        display += "╚╗╔╗║───║╔══╝─────║║\n"
        display += "─║║║╠╦═╗║╚══╦╦═╗╔═╝╠══╦═╗\n"
        display += "─║║║╠╣╔╝║╔══╬╣╔╗╣╔╗║║═╣╔╝\n"
        display += "╔╝╚╝║║║─║║──║║║║║╚╝║║═╣║\n"
        display += "╚═══╩╩╝─╚╝──╚╩╝╚╩══╩══╩╝\n"
        print(display)

    def create_extensions(self):
        if args.e:
            ext_list = self.extensions.split() 
            ext_list.insert(0,"")
            ext_list.insert(1,"/")
        else:
            ext_list = []
            ext_list.insert(0,"")
            ext_list.insert(1,"/")

        return ext_list

    def check_url(self):
        check = self.target[-1]
        if check == "/": 
            return self.target
        else:
            fixed_url = self.target + "/"
            return fixed_url

    def create_header(self):

        headers = {
            "Connection":"close"
        }

        return headers

    def options_and_wordlistset(self):
        print("Finding Pages:")

        original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
        pool = Pool(processes=int(self.threads)) 
        signal.signal(signal.SIGINT, original_sigint_handler)

        lines = []
        with open(self.file,'r') as wordlist_file: 
            for each_word in wordlist_file:
                lines.append(each_word.rstrip())

        if args.o:

            if args.b:
                print("Blacklisted Status Code: " + self.blacklist_status_code)
                file_write = open(self.output_file,"w")
                file_write.close()
                try:
                    start = pool.map_async(self.directory_finder_with_outputfile_and_blacklist_status_code,lines)
                except KeyboardInterrupt:
                    print("Bye Bye!")
                    pool.terminate()
                    exit()
                else:
                    pool.close()
                pool.join()  

            else:
                file_write = open(self.output_file,"w")
                file_write.close()
                try:
                    start = pool.map_async(self.directory_finder_with_outputfile,lines)
                except KeyboardInterrupt:
                    print("Bye Bye!")
                    pool.terminate()
                    exit()
                else:
                    pool.close()
                pool.join() 

        else:

            if args.b:
                print("Blacklisted Status Code: " + self.blacklist_status_code)
                try:
                    start = pool.map_async(self.directory_finder_with_blacklist_status_code,lines)
                except KeyboardInterrupt:
                    print("Bye Bye!")
                    pool.terminate()
                    exit()
                else:
                    pool.close()
                pool.join() 

            else:
                try:
                    start = pool.map_async(self.directory_finder_no_options,lines)
                except KeyboardInterrupt:
                    print("Bye Bye!")
                    pool.terminate()
                    exit()
                else:
                    pool.close()
                pool.join()

        print("Done!")

    def directory_finder_no_options(self,each_word):
        requests.packages.urllib3.disable_warnings()
                
        for ext in self.ext_list:
            sites = self.url + each_word + ext.strip()
            found = requests.get(sites, allow_redirects = False, verify=False,headers=self.headers) 

            if sites.find("#") != -1:
                continue
            elif found.status_code != 404:
                print("Found: ", found.url, "\tStatus Code:", found.status_code) 
                break
                
    def directory_finder_with_blacklist_status_code(self,each_word):
        requests.packages.urllib3.disable_warnings() 
                
        for ext in self.ext_list: 
            sites = self.url + each_word + ext.strip()
            found = requests.get(sites, allow_redirects = False, verify=False,headers=self.headers) 
            
            if sites.find("#") != -1:
                continue
            elif found.status_code != 404 and found.status_code != int(self.blacklist_status_code): 
                print("Found: ", found.url, "\tStatus Code:", found.status_code) 
                break                                                

    def directory_finder_with_outputfile(self,each_word):
        requests.packages.urllib3.disable_warnings() 
                
        for ext in self.ext_list:
            sites = self.url + each_word + ext.strip()  
            found = requests.get(sites, allow_redirects = False, verify=False,headers=self.headers) 
                    
            if sites.find("#") != -1:
                continue
            elif found.status_code != 404: 
                print("Found: ", found.url, "\tStatus Code:", found.status_code)  

                file_write = open(self.output_file,'a')
                file_write.write("Found: ")
                file_write.write(found.url)
                file_write.write("\tStatus Code: ")
                file_write.write(str(found.status_code))
                file_write.write("\n")
                file_write.close()

                break                                                                

    def directory_finder_with_outputfile_and_blacklist_status_code(self,each_word):
        requests.packages.urllib3.disable_warnings() 
                
        for ext in self.ext_list: 
            sites = self.url + each_word + ext.strip() 
            found = requests.get(sites, allow_redirects = False, verify=False,headers=self.headers)
                    
            if sites.find("#") != -1:
                continue
            elif found.status_code != 404 and found.status_code != int(self.blacklist_status_code): 
                print("Found: ", found.url, "\tStatus Code:", found.status_code)  

                file_write = open(self.output_file,'a')
                file_write.write("Found: ")
                file_write.write(found.url)
                file_write.write("\tStatus Code: ")
                file_write.write(str(found.status_code))
                file_write.write("\n")
                file_write.close()

                break                                                        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Brute Forcing Directories and Pages')

    parser.add_argument('-u', metavar='<Target URL>', help='target/host URL, E.G: -t http://findme.blah/', required=True)
    parser.add_argument('-e', metavar='<extensions>',help="Example: -e '.ext1 .ext2 .ext3'", required=False)
    parser.add_argument('-w', metavar='<wordlist file>',help="Example: -w list.txt", required=True)
    parser.add_argument('-o', metavar='<output file>',help="Example: -o output.txt", required=False)
    parser.add_argument('-b', metavar='<Blacklist Status Code>',help="Example: -b 500", required=False)
    parser.add_argument('-t', metavar='<Threads>',default="10",help="Example: -t 100. Default 10", required=False)

    args = parser.parse_args()

    try:
        Dir_Finder(args.u,args.w,args.e,args.o,args.b,args.t)
    except KeyboardInterrupt:
        print("Bye Bye") 
        exit()