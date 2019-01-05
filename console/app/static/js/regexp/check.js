
function check_input(strCheck)
{
	var strRegExpCheck = ''
	var strRegExpReplace = ''
	var strInfo = ''
    switch(strCheck)
    {
        case "_N":  //自然数集
			strRegExpCheck = '[0-9]+$'
            strRegExpReplace = '[^0-9]'
			strInfo = '自然数'
            break;
        case "_S":  //不含数字大写串
            strRegExpCheck = '[A-Z]+$'
            strRegExpReplace = '[^A-Z]'
			strInfo = '大写字母'
            break;
        case "SD":  //含数字串且字母开头的大写串
            strRegExpCheck = '^[A-Z][A-Z0-9]*$'
            strRegExpReplace = ''
			strInfo = '大写字母开头的字母数字串'
            break;
        case "_s":  //不含数字小写串
            strRegExpCheck = '[a-z]+$'
            strRegExpReplace = '[^a-z]'
			strInfo = '小写字母'
            break;
        case "sd":  //含数字串且字母开头的小写串
            strRegExpCheck = '^[a-z][a-z0-9]*$'
            strRegExpReplace = ''
			strInfo = '小写字母开头的字母数字串'
            break;
        case "_C":  //不含数字串(不判断大小写)
            strRegExpCheck = '[A-Za-z]+$'
            strRegExpReplace = '[^a-zA-Z]'
			strInfo = '字母串'
            break;
        case "CD":  //含数字串且字母开头的串(不判断大小写)
            strRegExpCheck = '^[a-zA-Z][a-zA-Z0-9]*$'
            strRegExpReplace = ''
			strInfo = '字母开头的字母数字串'
            break;
        case "_B":  //布尔
            ///^(true)|(false)$/.test('test')
            strRegExpCheck = '^(true)|(false)$'
            strRegExpReplace = '[^a-zA-Z]'
            break;
		default:
			break;
    }
	return [strRegExpCheck, strRegExpReplace, strInfo];
}

function prefixInteger(num, n) 
{
    return (Array(n).join(0) + num).slice(-n);
}
		
function onBlurEvent(id, strFormat)
{
	var inputValue = document.getElementById(id)
	if(inputValue)
	{
		nValueLen = inputValue.value.length
		nFrmLen = Number(strFormat.substr(2, 2))
		switch(strFormat.substr(0, 2))
		{
			case 'L0':
				if(nFrmLen > nValueLen)
					inputValue.value = prefixInteger(inputValue.value, nFrmLen)
				break
		}
	}
}

function onKeyUpEvent(inputName, strRegExpCheck, strRegExpReplace, strInfo)
{
	var inputValue = document.getElementById(inputName);
	var regExp = new RegExp(strRegExpCheck, 'g');

	if(!regExp.test(inputValue.value))
	{
		toastr.info(strInfo)
        var str = inputValue.value
        while(str.length > 0 && !regExp.test(str))
            str = str.substr(0, str.length - 1)
        inputValue.value = str
	}

	//regExp = new RegExp(strRegExpReplace, 'g');
	//inputValue.value=inputValue.value.replace(regExp, '');
}

function onCheckKeyUpEvent(id)
{
	var inputCheck = document.getElementById(id);
	var regExp = new RegExp('^(TX){1}(((_N)|(_S)|(SD)|(_s)|(sd)|(_C)|(CD)|(_B)){1})(([0-9]{3})|(___)){1}((([A-Z]{1})([A-Za-z0-9]{1})([0-9]{2}))|(____)){1}', 'g');
	if(!regExp.test(inputCheck.value))
		toastr.info('0-1两个字符固定为TX; 2-3两个字符是数据类型(_N:自然数、_S:大写字母、SD:大写字母和数字、_s:小写字母、sd:小写字母和数字、_C:大小写字母、CD:大小写字母和数字、_B:true或false); 4-6三个字符的十进制数是输入最大长度; 7-8两个字符是格式化类型(L0:左端补零);9-10两个字符的十进制数是补位数量')
}

function onBoolKeyUpEvent(inputName)
{
	var inputValue = document.getElementById(inputName);
	
	if(!(inputValue.value == 't' || inputValue.value == 'T' || inputValue.value == 'f' || inputValue.value == 'F'))
	{
		inputValue.value=''
		toastr.info('true|false')
	}
	else
	{
		switch(inputValue.value)
		{
			case 't':
			case 'T':
				inputValue.value = 'true'
				break;
			case 'f':
			case 'F':
				inputValue.value = 'false'
				break;
			default:
				inputValue.value = ''
		}
	}
}

