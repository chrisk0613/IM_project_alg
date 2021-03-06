#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
# import data.fixed.tool as tl
"""============================================================================#
input：
	LOWER 		- 日期j，班別集合ks，職位p，上班人數下限
	UPPER 		- 員工i，日子集合js，班別集合ks，排班次數上限
	PERCENT		- 日子集合，班別集合，要求占比，年資分界線
	DEMAND		- 日子j於時段t的需求人數
	E_POSITION 	- 擁有特定職稱的員工集合，POSI=1,…,nPOSI
	E_SENIOR 	- 達到特定年資的員工集合    
	DAYset 		- 通用日子集合 [all,Mon,Tue...]
	SHIFTset	- 通用的班別集合 [all,morning,noon,night...]

output：
[	'upper'/'lower'/'ratio',
	i_set,		#employee
	j_set,		#date
	k_set,		#work class
	n 			#umber
]	
============================================================================#"""

#計算平均需求人數（用以估計滿足限制所需人數）
def avgNeed(dates,classes, DAY,K,K_TIME,Need):
	avg_all = 0							#總平均需求人數
	for d in DAY[dates]:				#for all relative dates
		avg_day = 0							#本日各班別平均需求人數
		for k in K[classes]:				#for all relative class
			kt = K_TIME[k]
			avg_ = 0							#各班別本日平均需求
			for t in range(len(kt)):			#for each time perior in a class
				if kt[t]>0:							#若此班別包含此時段
					avg_ += Need[d][t]					#將本時段的預估人數加進班別平均
			avg_ = avg_/sum(kt)					#算出本日某班平均
			avg_day += avg_						#加進本日平均
		avg_day = avg_day/len(K[classes])	#算出本日平均
		avg_all += avg_day					#加進總平均
	avg_all = avg_all/len(DAY[dates])	#算出總平均	
	return avg_all

def takeNeck(alist):
	try:
		return alist[5]
	except:
		print('找不到項目 ',end='')
		print(alist,end='')
		print(' 的瓶頸程度參數')
		return None

def exchange(index1, index2, alist):
	buff = alist[index1]
	alist[index1] = alist[index2]
	alist[index2] = buff
	return None


#=============================================================================#
# main function

def LIMIT_ORDER(N, L, U, S, Need, POSI, SENIOR, DAY, K, DATES, K_TIME):
	# print(L)
	# print(POSI)
	limits = []
	#upper limit: (all), j_set, k_set, n
	for i in U:
		n = int(i[2])
		avg = avgNeed(i[0],i[1], DAY,K,K_TIME,Need)
		neck = float( n - avg )						#剩餘可動人手 = 上限人數 - 平均需求人數 (很可能是負數)
		limits.append([ 'upper', POSI['任意'], DAY[i[0]], K[i[1]], n, neck])

	#lower limit: j, k_set, i(position), n
	# for i in L:
	# 	n = int(i[3])
	# 	neck = float( len(POSI[i[2]]) - n )
	# 	limits.append([ 'lower', POSI[i[2]], [int(i[0])], K[i[1]], n, neck])

	#senior limit: j_set, k_set, n, i(senior) 
	for ii in range(len(S)):	#because we need to get SENIOR which is without index
		i = S[ii]
		n = float(i[2])
		#計算瓶頸程度：總可用人數 - 需求人數(n*平均需求人數)
		neck = len(SENIOR[ii]) - n*avgNeed(i[0], i[1], DAY,K,K_TIME,Need)	#瓶頸程度=剩餘可動人手
		limits.append([ 'ratio', SENIOR[ii], DAY[i[0]], K[i[1]], n, neck])

	#sort
	limits.sort(key=takeNeck, reverse=False)

	#change order
	main = [limits]
	nl = len(limits)
	for dis in range(1, nl):							#dis = 要交換的兩項的距離(從1開始)
		for i in range(nl-1):							#第一個要交換項的index
			ii = i+dis
			if ii >= nl:								#要換的超過尾端，則不換，跳出
				break
			elif len(main) >= N:						#現有的排序數量比要的還要多
				break
			else:
				buff = limits							#buff存放交換過的序列
				exchange(i, ii, buff)
			main.append(buff)

	#return
	print('\nLIMIT_ORDER(): return',len(main),'kinds of order\n')
	return main



"""
1234
#dis=1
2134
1324
1243
#dis=2
3124
1432
#dis=3
4231

#other
1234_
1243_
1324_
1342
1423
1432_

2134_
2143
2314
2341
2413
2431

3124_
3142
3214
3241
3412
3421

4123
4132
4213
4231_
4312
4321
"""