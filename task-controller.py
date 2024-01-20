import os, time, platform, psutil, subprocess, mysql.connector

def folder_opener(path):
	global smf_path
	l_files=[]
	for j in os.listdir(path):
		if os.path.splitext(j)[1] == "" and ".ini" not in j:
			flst = folder_opener(path+j+"/")
			l_files.extend(flst)
		else:
			l_files.append(path[len(smf_path):] + j)
	l_files = list(set(l_files))

	return l_files

def isrunning(name, id = False):
	a = str(subprocess.check_output("tasklist /fo csv")).split(r'\r\n')
	lst = []
	for i in range(1,len(a)-1):													#Lists all running tasks
		lst.append(a[i].split("\",\""))
	l_apps = []
	for i in lst:																#Lists matching tasks
		i[0] = i[0][1:]
		if name.lower() == i[0].lower() or (name.lower()+".exe") == i[0].lower():
			if id == True:	return True,[i[1]]
			else: return True,[]
		elif name.lower() in i[0].lower() and len(name) >= 4 and len(name)/len(i[0][:4]) >= 0.3 and i[0] not in [n[0] for n in l_apps]:
			l_apps.append(i)
	if len(l_apps) > 0:
		return False,l_apps
	else:
		return False,[]

def run(name):

	try:
		os.startfile(name)
		return
	except:
		try:
			os.startfile(smf_path+name)
			print("Starting App")
			return
		except:
			pass
	l_dir = folder_opener(smf_path)

	try:
		l_apps = []
		for p in l_dir:
			if name.lower() == os.path.splitext(p)[0].lower():
				os.startfile(smf_path + p)
				print("Starting App")
				return
			elif name.lower() in os.path.splitext(p)[0].lower() and (len(name)/len(os.path.splitext(p)[0]) >= 0.5 or name.lower() in os.path.splitext(p)[0].lower().split("/")[-1]):
				l_apps.append(p)
		
		if len(l_apps) > 0:
			print("Did you mean: ")
			for i in range(len(l_apps)):
				print(str(i+1) + "> ", l_apps[i].split("/")[-1])
			os.startfile(smf_path + l_apps[int(input("\n>>> "))-1])
			print("Starting App")
		else:
			print("App not Found")
	except:
		print("App not Found")

def close(name):
	ir,l = isrunning(name, id=True)
	if ir == False:
		print("App isn't Running")
	elif ir == True:
		psutil.Process(int(l[0])).kill()
		print("App Terminated")
	else:
		for i in range(len(l)):
			print(str(i+1) + "> ", l[i][0])
		i = int(input("Enter your choice: ")) - 1
		try:
			psutil.Process(int(l[i][1])).kill()
			print("App Terminated")
		except: print("App not Found")

def sql_reader(csr, show = "d", tb_nm = ""):
	l = []
	if show == "d":
		csr.execute("show databases")
	elif show == "t":
		csr.execute("show tables")
	else:
		csr.execute(show)
	for i in csr:
		l.append(i[0])
	return l

def check_schedule():
	csr.execute("select * from tb_apps")
	l = csr.fetchall()
	csr.execute("select * from tb_sch")
	for i in csr.fetchall():
		if time.strftime("%H,%M") == str(i[2])[:-3] and isrunning(l[i[0]][1]) == False:
			run(i[1])

def check_timer():
	csr.execute("select * from tb_apps")
	l = csr.fetchall()
	csr.execute("select * from tb_tmr")
	for i in csr.fetchall():
		if time.strftime("%H,%M") == str(i[2])[:-3] and isrunning(l[i[0]][1]):
			close(i[1])

def main():
	##################     INIT     ##################

	while True:
		print("\nWhat would you like to do?")
		l_optns = ["Edit Controlled Apps", "Manage Apps", "System Info"]
		for i in range(len(l_optns)):
			print(str(i+1) + "> ", l_optns[i])
		ipt = int(input(">>> "))
		print()

		if ipt == 1:
			l_optns = ["Add New App Record", "Remove an App Record", "Change an App Record", "View all Apps"]
			for i in range(len(l_optns)):
				print(str(i+1) + "> ", l_optns[i])
			opt = int(input(">>> "))
			print()

			if opt == 1:
				l_apps = []

				for i in range(1,len(ap_clm)):
					if ap_clm[i] in ("schedule", "timer"):
						ipt = input(ap_clm[i].capitalize()+": 1 -> yes, 0 -> no\n>>> ")
					else:
						ipt = input(ap_clm[i].capitalize()+"\n>>> ")
					if ipt == "":
						l_apps.append("null")
					else:
						l_apps.append(ipt)
				s_run = f"insert into tb_apps values(null, '{l_apps[0]}', '{l_apps[1]}', {l_apps[2]}, {l_apps[3]})"
				csr.execute(s_run)
				csr.execute("select * from tb_apps")
				line_no = csr.fetchall()[-1][0]
				
				if int(l_apps[2]) == 1:
					print()
					l_sc = []
					for i in range(1,len(sc_clm)):
						if sc_clm[i] == "start_at":
							ipt = input(sc_clm[i].capitalize()+": time format -> HH:MM:SS\n>>> ")
						elif sc_clm[i] == "occurence":
							ipt = input(sc_clm[i].capitalize()+": 1 -> yes, 0 -> no, day format -> MTWTFSS\n>>> ")
						else:
							ipt = input(sc_clm[i].capitalize()+"\n>>> ")
						if ipt == "":
							l_sc.append("null")
						else:
							l_sc.append(ipt)

					s="\\"
					l_sc[0] = l_sc[0].replace(s, s+s)
					s_run = f"insert into tb_sch values({line_no}, '{l_sc[0]}', '{l_sc[1]}', {l_sc[2]}, '{l_sc[3]}')"
					csr.execute(s_run)

				if int(l_apps[3]) == 1:
					print()
					l_tm = []
					for i in range(1,len(tm_clm)):
						if tm_clm[i] in ("close_at", "daily_limit"):
							ipt = input(tm_clm[i].capitalize()+", time format -> HH:MM:SS\n>>> ")
						else:
							ipt = input(tm_clm[i].capitalize()+"\n>>> ")
						if ipt == "":
							l_tm.append("null")
						else:
							l_tm.append(ipt)

					s_run = f"insert into tb_tmr values({line_no}, '{l_tm[0]}', '{l_tm[1]}', '{l_tm[2]}', '{l_tm[3]}')"
					csr.execute(s_run)

			if opt == 2:
				rmv = input("Enter App Name\n>>> ")
				csr.execute("select * from tb_apps")
				for n in csr.fetchall():
					print(n[1], rmv)
					if n[1].lower() == rmv.lower():
						csr.execute(f"delete from tb_apps where id = {n[0]}")
						csr.execute(f"delete from tb_sch where id = {n[0]}")
						csr.execute(f"delete from tb_tmr where id = {n[0]}")

			if opt == 3:
				app = input("Enter App Name\n>>> ").lower()
				clm = input("Enter the Field\n>>> ").lower()
				new = input("Enter the New Data\n>>> ")
				a=0
				csr.execute("select * from tb_apps")
				s = csr.fetchall()
				for i in s:
					if i[1].lower() == app:
						app = i[0]
				if clm in ap_clm:
					csr.execute(f"update tb_apps set {clm} = '{new}' where id = {app}")
				elif clm in sc_clm:
					csr.execute(f"update tb_sch set {clm} = '{new}' where id = {app}")
				elif clm in tm_clm:
					csr.execute(f"update tb_tmr set {clm} = '{new}' where id = {app}")
				else:
					print("Incorrect Data")
			db.commit()

			if opt in range(1,5):
				
				csr.execute("select * from tb_apps")
				s = csr.fetchall()
				print("\nAll Apps: ")
				if len(s) >= 1:
					print("| ", end="")
					[print(str(x), end = " | ") for x in ap_clm]
					[[print("\n| ", end="\n"), [print(str(x), end = " | ") for x in n]] for n in s]
					print()
				else:
					print("No Apps")
				
				csr.execute("select * from tb_sch")
				s = csr.fetchall()
				print("\nSchedule: ")
				if len(s) >= 1:
					print("| ", end="")
					[print(str(x), end = " | ") for x in sc_clm]
					[[print("\n| ", end=""), [print(str(x), end = " | ") for x in n]] for n in s]
					print()
				else:
					print("No Apps")
				
				csr.execute("select * from tb_tmr")
				s = csr.fetchall()
				print("\nTimer: ")
				if len(s) >= 1:
					print("| ", end="")
					[print(str(x), end = " | ") for x in tm_clm]
					[[print("\n| ", end=""), [print(str(x), end = " | ") for x in n]] for n in s]
					print()
				else:
					print("No Apps")

		elif ipt == 2:
			l_optns = ["Start an App", "Close an App", "Check if Running"]
			for i in range(len(l_optns)):
				print(str(i+1) + "> ", l_optns[i])
			opt = int(input(">>> "))
			print()

			if opt == 1:
				name = input("Enter App Name\n>>> ")
				run(name)

			elif opt == 2:
				name = input("Enter App Name\n>>> ")
				close(name)

			elif opt == 3:
				name = input("Enter App Name\n>>> ")
				ir,l = isrunning(name)
				if ir == True:
					print(name, "is Running...")
				else:
					print(name, "isn't Running...")
					if len(l) > 0:
						print("Similar Programs which are Running: ")
						for i in l:
							print(str(i+1) + ">", ir[i][0])

		elif ipt == 3:
			x = platform.uname()
			print("os: ", x.system)
			print("version: ", x.version)
			print("name: ", x.node)
			print("processor architecture: ", x.machine)
			print("processor: ", x.processor)
			print("available memory: ", round(psutil.virtual_memory().available/1024**3, 2), "GB /", round(psutil.virtual_memory().total/1024**3, 2), "GB")
			info = (input("Open Task Manager & DirectX Diagnostics for more Info(y/n)\n>>> ")).lower()
			if info == "y":
				os.startfile("taskmgr")
				os.startfile("dxdiag")

		elif ipt == 4:
			print("Checking...")
			while True:
				time.sleep(15)
				check_schedule()
				check_timer()

if __name__ == "__main__":

	smf_path = "C:/ProgramData/Microsoft/Windows/Start Menu/Programs/"
	db = mysql.connector.connect(host="localhost", user="root", password="Vam#090905")
	csr = db.cursor(buffered = True)
	ap_clm = ["id", "name", 		"description",	"schedule", 	"timer"]
	sc_clm = ["id", "path", 		"start_at", 	"occurence", 	"tag"]
	tm_clm = ["id", "process_name", 	"close_at", 	"daily_limit", 	"tag"]

	if "db_apps" not in sql_reader(csr):
  		csr.execute("create database db_apps")

	csr.execute("use db_apps")
	if "tb_apps" not in sql_reader(csr, "t"):
 		csr.execute(f"create table tb_apps({ap_clm[0]} int not null auto_increment  primary key, \
		{ap_clm[1]} varchar(50) not null, {ap_clm[2]} varchar(100), {ap_clm[3]} bit, {ap_clm[4]} bit)")
	if "tb_sch" not in sql_reader(csr, "t"):
		csr.execute(f"create table tb_sch({sc_clm[0]} int not null primary key, \
		{sc_clm[1]} varchar(250) not null, {sc_clm[2]} time, {sc_clm[3]} char(7), {sc_clm[4]} varchar(50))")
	if "tb_tmr" not in sql_reader(csr, "t"):
		csr.execute(f"create table tb_tmr({tm_clm[0]} int not null primary key, \
		{tm_clm[1]} varchar(50) not null, {tm_clm[2]} time, {tm_clm[3]} time, {tm_clm[4]} varchar(50))")
	
	main()
