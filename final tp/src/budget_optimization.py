# This file uses a recursive budget optimizing algorithm I wrote to generate all possible 
# Combinations of webscraped products that are within the desired budget
import rec

def sortRecsByPOI(recs, n):
	result = [[] for i in range(n)]
	for rec in recs:
		result[recs.poi_id].append(rec)
	return result

def getAllOptions(recs, n, budget):
	if n == 0:
		recs = recs[0]
		if budget == None: return [[i] for i in sorted(recs, key = lambda var: var.price)]
		return [[i] for i in sorted([rec for rec in recs if rec.price <= budget], key = lambda var: var.price)]
	else:
		curr = recs[n]
		if budget == None: curr = sorted(curr, key = lambda var: var.price)
		else: curr = sorted([c for c in curr if c.price <= budget], key = lambda var: var.price)
		results = []
		rec_sets = getAllOptions(recs, n-1, budget)
		for rec in rec_sets:
			rec_sum = sum(r.price for r in rec)
			for c in curr:
				if budget == None:
					if c not in rec and len(rec) != n + 1: results.append(rec + [c])
				else:
					if float(c.price) + float(rec_sum) <= budget and c not in rec and len(rec) != n + 1: results.append(rec + [c])
		return results





