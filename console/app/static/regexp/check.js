
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
        case "N+":  //正整数集
            //strRegExp = '^[1-9]\\d*$'
			strInfo = '正整数'
            break;
        case "_Z":  //整数集
            //strRegExp = '^-?[1-9]\\d*$'
			strInfo = '整数'
            break;
        case "_R":  //实数集
            //strRegExp = '^0\\.\\d+$|^[1-9]+(\\.\\d+)?$'
			strInfo = '实数'
            break;
        case "_S":  //不含数字大写串
            strRegExpCheck = '[A-Z]+$'
            strRegExpReplace = '[^A-Z]'
			strInfo = '大写字母'
            break;
        case "SD":  //含数字串且字母开头的大写串
            //strRegExp = '^(?!^[A-Z][A-Z0-9]*$)'
			strInfo = '大写字母开头的字母数字串'
            break;
        case "_s":  //不含数字小写串
            strRegExpCheck = '[a-z]+$'
            strRegExpReplace = '[^a-z]'
			strInfo = '小写字母'
            break;
        case "sd":  //含数字串且字母开头的小写串
            //strRegExp = '^[a-z][a-z0-9]*$'
			strInfo = '小写字母开头的字母数字串'
            break;
        case "_C":  //不含数字串(不判断大小写)
            strRegExpCheck = '[A-Za-z]+$'
            strRegExpReplace = '[^a-zA-Z]'
			strInfo = '字母串'
            break;
        case "CD":  //含数字串且字母开头的串(不判断大小写)
            //strRegExp = '^[a-zA-Z][a-zA-Z0-9]*$'
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

function onKeyUpEvent(inputName, strRegExpCheck, strRegExpReplace, strInfo)
{
	var inputValue = document.getElementById(inputName);
	var regExp = new RegExp(strRegExpCheck, 'g');

	if(!regExp.test(inputValue.value))
	{
		toastr.info(strInfo)
	}
	regExp = new RegExp(strRegExpReplace, 'g');
	inputValue.value=inputValue.value.replace(regExp, '');
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

