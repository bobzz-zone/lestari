# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import datetime, requests

class WorklogTesting(Document):
	def jamPulangOperator(self,tanggal:str):
		# get day name from tanggal
		day_name = datetime.datetime.strptime(tanggal, "%Y-%m-%d").strftime("%A")
		# case day_name
		match day_name:
			case "Friday":
				return "16:10:00"
			case _:
				return "15:40:00"

	def getEmployeeOvertime(self,idEmployee:int,transdate:str):
		payload = {
			"idEmployee":idEmployee,
			"transdate":transdate
		}
		# payload = {
		# 	"idEmployee":1598,
		# 	"transdate":"2024-05-10"
		# }
		req = requests.get('http://192.168.3.25/api/v1/lestari-worklog/get-employee-overtime', params=payload)
		if req.status_code != 200:
			return False,None
		res = req.json()
		return True,res
	
	# Sesudah Save
	def validate(self):
		worklog = self
		waktu_mulai = datetime.datetime.strptime(worklog.waktu_mulai.split('.')[0], "%Y-%m-%d %H:%M:%S")
		waktu_selesai = datetime.datetime.strptime(worklog.waktu_selesai.split('.')[0], "%Y-%m-%d %H:%M:%S")
		have_pause_pulang = False
		for item in worklog.list_pause:
			keterangan_pause_name = item.keterangan_pause
			# get keterangan_pause_name from Keterangan Pause
			keterangan_pause_name = frappe.db.get_value('Keterangan Pause', {'name': keterangan_pause_name}, 'keterangan')
			if keterangan_pause_name == 'Pulang':
				have_pause_pulang = True
				break

		if (waktu_mulai.date() != waktu_selesai.date()):
			if have_pause_pulang:
				# frappe.msgprint("Punya waktu pulang, Tidak akan diproses")
				return
			tanggal_mulai = waktu_mulai.strftime("%Y-%m-%d")
			tanggal_selesai = waktu_selesai.strftime("%Y-%m-%d")
			# Set Default jam_pulang
			jam_pulang = datetime.datetime.strptime(f"{tanggal_mulai} {self.jamPulangOperator(tanggal_mulai)}", "%Y-%m-%d %H:%M:%S")
			
			check_success,emploee_overtime = self.getEmployeeOvertime(idEmployee=worklog.employee_id,transdate=tanggal_mulai)
			if check_success:
				jam_pulang = emploee_overtime['data']['overtime_end']
				# convert jam_pulang to datetime
				jam_pulang = datetime.datetime.strptime(jam_pulang, "%Y-%m-%d %H:%M:%S")
				# substract jam_pulang 20 minutes
				jam_pulang = jam_pulang - datetime.timedelta(minutes=20)

			# get difference between waktu_mulai and jamPulang as yesterdayWorkingtime
			yesterdayWorkingtime = round(jam_pulang.timestamp() - waktu_mulai.timestamp())

			# Get Workstation by Operation
			workstation = frappe.db.get_value('Operation', {'name': worklog.operation}, 'workstation')
			
			# Get Keterangan Pause with keterangan is 'Pulang' and workstation is equal with workstation
			keterangan_pause = frappe.db.get_value('Keterangan Pause', {'keterangan': 'Pulang', 'workstation': workstation}, 'name')

			# check if worklog.waktu_selesai is less than worklog.waktu_selesai at 07:40:00
			if waktu_selesai < datetime.datetime.strptime(f"{waktu_selesai.date()} 07:40:00", "%Y-%m-%d %H:%M:%S"):
				# waktu_resume dibawah jam 8. Update waktu Selesai to 07:40:00
				waktuSelesai = datetime.datetime.strptime(f"{waktu_selesai.date()} 07:40:00", "%Y-%m-%d %H:%M:%S")
				lamaPause = round(waktuSelesai.timestamp() - jam_pulang.timestamp())
				totalDetik = lamaPause + worklog.total_detik_pause + yesterdayWorkingtime
				totalDetikWorking = yesterdayWorkingtime
				totalDetikPause = lamaPause

				# update worklog
				worklog.waktu_selesai = waktuSelesai
				worklog.total_detik_pause = totalDetikPause
				worklog.total_detik_working = totalDetikWorking
				worklog.total_detik = totalDetik
				worklog.append("list_pause",{
					"start_pause":jam_pulang,
					"end_pause":waktuSelesai,
					"keterangan_pause":keterangan_pause,
					"total_seconds":lamaPause
				})
				# worklog.flags.ignore_permissions = True
				# save worklog
				# worklog.save()
				return
			else:
				# waktu_resume dibawah jam 8. Update waktu Selesai to 07:40:00
				waktuSelesai = datetime.datetime.strptime(f"{waktu_selesai.date()} 07:40:00", "%Y-%m-%d %H:%M:%S")
				lamaPause = round(waktuSelesai.timestamp() - jam_pulang.timestamp())
				todayWorkingtime = round(waktu_selesai.timestamp() - waktuSelesai.timestamp())
				totalDetik = lamaPause + worklog.total_detik_pause + yesterdayWorkingtime + todayWorkingtime
				totalDetikWorking = yesterdayWorkingtime + todayWorkingtime
				totalDetikPause = lamaPause + worklog.total_detik_pause
				
				# update worklog
				worklog.total_detik_pause = totalDetikPause
				worklog.total_detik_working = totalDetikWorking
				worklog.total_detik = totalDetik
				worklog.append("list_pause",{
					"start_pause":jam_pulang,
					"end_pause":waktuSelesai,
					"keterangan_pause":keterangan_pause,
					"total_seconds":lamaPause
				})
				# worklog.flags.ignore_permissions = True
				# save worklog
				# worklog.save()
				return

		return

	def insertWIPOperationMovement(self,operation:str, employee:str, spko:str, weight:float, pcs:int, type:str):
		newWIPOperationMovement = frappe.new_doc('WIP Operation Movement')
		newWIPOperationMovement.operation = operation
		newWIPOperationMovement.employee = employee
		# Create current date
		current_date = datetime.datetime.now()
		newWIPOperationMovement.transdate = current_date.strftime("%Y-%m-%d")
		newWIPOperationMovement.spko = spko
		newWIPOperationMovement.work_log = self.name
		newWIPOperationMovement.weight = weight
		newWIPOperationMovement.pcs = pcs
		newWIPOperationMovement.type = type
		newWIPOperationMovement.flags.ignore_permissions = True
		newWIPOperationMovement.save()

	def on_submit(self):
		# TestingFunction()
		totalWeight = 0
		totalPcs = self.total_pcs
		for row in self.list_spko:
			# frappe.db.sql("""UPDATE `tabSPKO` SET status = 'Done' WHERE name = '{}' """.format(row.spko))

			# set spko work log
			frappe.db.set_value('SPKO', {'name': row.spko}, 'work_log', self.name)
			# set spko status
			frappe.db.set_value('SPKO', {'name': row.spko}, 'status', 'Done')
			totalWeight += float(frappe.db.get_value('SPKO', {'name': row.spko}, 'berat'))
			# frappe.db.commit()

		if self.next_operation is not None:
			nextOperation = self.next_operation
			for spko in self.list_spko:
				weight = float(frappe.db.get_value('SPKO', {'name': spko.spko}, 'berat'))
				pcs = int(frappe.db.get_value('SPKO', {'name': spko.spko}, 'jumlah_pcs'))

				self.insertWIPOperationMovement(self.operation, self.employee, spko.spko, weight*-1, pcs*-1, 'OUT')
				self.insertWIPOperationMovement(nextOperation, self.employee, spko.spko, weight, pcs, 'IN')
		else:
			# Get Workstation from current operation
			workstation = frappe.db.get_value('Operation', {'name': self.operation}, 'workstation')
			# list workstation for available stock WIP Operation
			availableWorkstation = ['Poles'] 
			if workstation in availableWorkstation:
				# get next operation from Operation
				nextOperation = frappe.db.get_value('Operation', {'name': self.operation}, 'next_operation')
				for spko in self.list_spko:
					weight = float(frappe.db.get_value('SPKO', {'name': spko.spko}, 'berat'))
					pcs = int(frappe.db.get_value('SPKO', {'name': spko.spko}, 'jumlah_pcs'))

					self.insertWIPOperationMovement(self.operation, self.employee, spko.spko, weight*-1, pcs*-1, 'OUT')
					if nextOperation != 'Transfer Material':
						self.insertWIPOperationMovement(nextOperation, self.employee, spko.spko, weight, pcs, 'IN')
		
	def on_trash(self):
		wipInserted = frappe.db.get_list('WIP Operation Movement', filters={'work_log': self.name}, fields=['name'])
		for item in wipInserted:
			# get doc wip
			wip = frappe.get_doc('WIP Operation Movement', item.name)

			# update remove Worklog from WIP Operation Movement
			frappe.db.set_value('WIP Operation Movement', {'name': item.name}, 'work_log', None)
		
			newWIPOperationMovement = frappe.new_doc("WIP Operation Movement")
			newWIPOperationMovement.employee = wip.employee
			newWIPOperationMovement.spko = wip.spko
			newWIPOperationMovement.operation = wip.operation
			newWIPOperationMovement.transdate = frappe.utils.now()
			newWIPOperationMovement.weight = wip.weight*-1
			newWIPOperationMovement.pcs = wip.pcs*-1
			newWIPOperationMovement.type = "OUT" if wip.type == "IN" else "IN"
			newWIPOperationMovement.flags.ignore_permissions = True
			newWIPOperationMovement.save()
			frappe.db.commit()


# @frappe.whitelist()
# def TestingFunction():
# 	worklog = frappe.get_doc("Work log Testing", "WL-456324")
# 	waktu_mulai = worklog.waktu_mulai
# 	waktu_selesai = worklog.waktu_selesai
# 	if (waktu_mulai.date() != waktu_selesai.date()):
# 		tanggal_mulai = waktu_mulai.strftime("%Y-%m-%d")
# 		tanggal_selesai = waktu_selesai.strftime("%Y-%m-%d")
# 		# Set Default jam_pulang
# 		jam_pulang = datetime.datetime.strptime(f"{tanggal_mulai} {jamPulangOperator(tanggal_mulai)}", "%Y-%m-%d %H:%M:%S")
		
# 		check_success,emploee_overtime = getEmployeeOvertime(idEmployee=worklog.employee_id,transdate=tanggal_mulai)
# 		if check_success:
# 			jam_pulang = emploee_overtime['data']['overtime_end']
# 			# convert jam_pulang to datetime
# 			jam_pulang = datetime.datetime.strptime(jam_pulang, "%Y-%m-%d %H:%M:%S")
# 			# substract jam_pulang 20 minutes
# 			jam_pulang = jam_pulang - datetime.timedelta(minutes=20)

# 		# get difference between waktu_mulai and jamPulang as yesterdayWorkingtime
# 		yesterdayWorkingtime = round(jam_pulang.timestamp() - waktu_mulai.timestamp())

# 		# Get Workstation by Operation
# 		workstation = frappe.db.get_value('Operation', {'name': worklog.operation}, 'workstation')
		
# 		# Get Keterangan Pause with keterangan is 'Pulang' and workstation is equal with workstation
# 		keterangan_pause = frappe.db.get_value('Keterangan Pause', {'keterangan': 'Pulang', 'workstation': workstation}, 'name')

# 		# check if worklog.waktu_selesai is less than worklog.waktu_selesai at 07:40:00
# 		if worklog.waktu_selesai < datetime.datetime.strptime(f"{worklog.waktu_selesai.date()} 07:40:00", "%Y-%m-%d %H:%M:%S"):
# 			# waktu_resume dibawah jam 8. Update waktu Selesai to 07:40:00
# 			waktuSelesai = datetime.datetime.strptime(f"{worklog.waktu_selesai.date()} 07:40:00", "%Y-%m-%d %H:%M:%S")
# 			lamaPause = round(waktuSelesai.timestamp() - jam_pulang.timestamp())
# 			totalDetik = lamaPause + worklog.total_detik_pause + yesterdayWorkingtime
# 			totalDetikWorking = yesterdayWorkingtime
# 			totalDetikPause = lamaPause

# 			# update worklog
# 			worklog.waktu_selesai = waktuSelesai
# 			worklog.total_detik_pause = totalDetikPause
# 			worklog.total_detik_working = totalDetikWorking
# 			worklog.total_detik = totalDetik
# 			worklog.append("list_pause",{
# 				"start_pause":jam_pulang,
# 				"end_pause":waktuSelesai,
# 				"keterangan_pause":keterangan_pause,
# 				"total_seconds":lamaPause
# 			})
# 			worklog.flags.ignore_permissions = True
# 			# save worklog
# 			worklog.save()
# 			return
# 		else:
# 			# waktu_resume dibawah jam 8. Update waktu Selesai to 07:40:00
# 			waktuSelesai = datetime.datetime.strptime(f"{worklog.waktu_selesai.date()} 07:40:00", "%Y-%m-%d %H:%M:%S")
# 			lamaPause = round(waktuSelesai.timestamp() - jam_pulang.timestamp())
# 			todayWorkingtime = round(worklog.waktu_selesai.timestamp() - waktuSelesai.timestamp())
# 			totalDetik = lamaPause + worklog.total_detik_pause + yesterdayWorkingtime + todayWorkingtime
# 			totalDetikWorking = yesterdayWorkingtime + todayWorkingtime
# 			totalDetikPause = lamaPause + worklog.total_detik_pause
			
# 			# update worklog
# 			worklog.total_detik_pause = totalDetikPause
# 			worklog.total_detik_working = totalDetikWorking
# 			worklog.total_detik = totalDetik
# 			worklog.append("list_pause",{
# 				"start_pause":jam_pulang,
# 				"end_pause":waktuSelesai,
# 				"keterangan_pause":keterangan_pause,
# 				"total_seconds":lamaPause
# 			})
# 			worklog.flags.ignore_permissions = True
# 			# save worklog
# 			worklog.save()
# 			return

# 	return