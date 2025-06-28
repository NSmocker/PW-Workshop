--102
lua_glb = {}

function lua_glb:check_md5(mapid)
	local maps = {}

	-- local files = {}
	-- files["Maps\\a14\\a14.ecbsd"] = "72771F66BB0845E5E33A36BA799A0242";
	-- files["Maps\\a14\\a14_1.t2bk"] = "BE0B61DDE3ACF5D724FA2F8E1360A97C";
	-- files["Maps\\a14\\bsdata\\1.dat"] = "66CAACCCF43306C67B19880137767155";	
	-- files["Maps\\a14\\a14.ecwld"] = "BE336CEB717A04BEB42EC28FCB1AFFD9";
	-- files["Maps\\a14\\a14.trn2"] = "C1BCE2047E81D41F45F073EDBBBBCB17";		
	-- maps["a14"] = files;

		local files_to_check = maps[string.lower(mapid)]
	if files_to_check == nil then
		return true
	end

	local f, m
	for f,m in pairs(files_to_check) do
		md5 = GlobalApi.lua_glb_CalcFileMd5(f)
		if string.lower(m) ~= string.lower(md5) then
			return false
		end	 
	end
	
 	return true
end