var questions = [
  {
    title: "过年亲戚聚会，长辈突然当众问你「读的什么大学啊？」，你的第一反应是？",
    dim: 3,
    options: [
      { text: "淡定报出学校全名，等着长辈的夸奖和羡慕", val: "T" },
      { text: "赶紧打哈哈说「就普通学校啦」，火速转移话题", val: "N" }
    ]
  },
  {
    title: "同学群里疯狂晒985/211考研上岸通知书，你的第一反应是？",
    dim: 2,
    options: [
      { text: "立刻翻出考研资料，今年必须卷个top校上岸", val: "P" },
      { text: "默默关掉群聊，卷不动了，躺平也挺好", val: "B" }
    ]
  },
  {
    title: "应届生找工作，你最核心的筛选标准是？",
    dim: 1,
    options: [
      { text: "公司title、行业前景、晋升空间，必须有长期发展", val: "A" },
      { text: "双休、不加班、五险一金足额交，能按时下班就行", val: "E" }
    ]
  },
  {
    title: "刷到「学历定终身，专科生这辈子就完了」的短视频，你的第一想法是？",
    dim: 4,
    options: [
      { text: "心里咯噔一下，完了，我这辈子是不是就这样了", val: "I" },
      { text: "纯纯放屁，我命由我不由学历", val: "O" }
    ]
  },
  {
    title: "如果能重来一次高考，你会做出什么选择？",
    dim: 1,
    options: [
      { text: "不卷了，选个好就业的专科，早毕业早赚钱", val: "E" },
      { text: "往死里学，必须考上top985，不留一点遗憾", val: "A" }
    ]
  },
  {
    title: "朋友给你介绍对象，对方第一句问「你是什么学历？」，你会？",
    dim: 3,
    options: [
      { text: "立刻报出自己的学校title，心里默默掂量对方配不配", val: "T" },
      { text: "直接回「学历很重要吗？先聊聊人不行？」", val: "N" }
    ]
  },
  {
    title: "身边的朋友都在二战/三战考研，只有你直接找了工作，你会觉得？",
    dim: 4,
    options: [
      { text: "完全无所谓，他们卷学历，我先赚第一桶金", val: "O" },
      { text: "有点焦虑，会不会不考研，这辈子就被落下了", val: "I" }
    ]
  },
  {
    title: "公司招聘，你看到一个专科生能力远超同岗985应届生，你会觉得？",
    dim: 2,
    options: [
      { text: "太正常了，学历和能力本来就不是一回事", val: "B" },
      { text: "有点离谱，985的学历怎么还比不过专科生", val: "P" }
    ]
  },
  {
    title: "毕业5年同学聚会，你最不想聊的话题是？",
    dim: 4,
    options: [
      { text: "薪资、学历、职级，怕自己混得不好，对不起当年的学校", val: "I" },
      { text: "完全没在怕的，什么都能聊，反正日子是自己过的", val: "O" }
    ]
  },
  {
    title: "对于「第一学历」，你的看法是？",
    dim: 3,
    options: [
      { text: "就是一张废纸，我能创造的价值，比这张纸重要一万倍", val: "N" },
      { text: "是一辈子的烙印，考不上好本科，读再好的研也有遗憾", val: "T" }
    ]
  },
  {
    title: "毕业三年后的同学聚会上，你希望自己是什么状态？",
    dim: 1,
    options: [
      { text: "不管怎样，title和薪资必须拿得出手，让所有人看到我在往上走", val: "A" },
      { text: "有份稳定工作就行，生活规律，该吃吃该喝喝，不追求出人头地", val: "E" }
    ]
  },
  {
    title: "面试官说「我们团队都是985/海归」，你的第一反应是？",
    dim: 2,
    options: [
      { text: "心里开始比较自己和他们的学历，暗暗较劲怎么在这群人中脱颖而出", val: "P" },
      { text: "无所谓，团队什么学历跟我没关系，干好自己的活就行", val: "B" }
    ]
  }
];

var results = {
  "EBNI": {
    name: "嘴硬心虚侠",
    img: "嘴硬心虚侠.jpg",
    desc: "适配人群：大专/高职毕业生、早入社会但嘴硬心虚的纠结实干派<br><br>嘴上说着「学历不重要」，回了家翻同学朋友圈翻到凌晨三点。躺平是社交面具，脱敏是自我保护，但内耗是真实日常。白天发朋友圈「打工人的快乐你不懂」，晚上偷偷搜「学历提升哪个机构靠谱」。卷不动、躺不平、放不下、睡不好，主打一个精神分裂式生存。",
    quote: "嘴上说躺平，心里在翻江倒海，我这不是佛系，是佛系精分。"
  },
  "EBNO": {
    name: "野生特种兵",
    img: "野生特种兵.jpg",
    desc: "适配人群：大专/高职毕业生、早入社会的本科毕业生、拒绝学历内卷的实干派<br><br>读书三年，不如社会三年摸爬滚打。18岁就懂了学历不是唯一出路，22岁已经攒下了同龄人没有的存款和生存技能。嘴上偶尔吐槽「没学历找工作好难」，心里门清「光有学历没本事也没用」。职场里的万能补位王，什么都能干，什么都敢闯，主打一个光脚不怕穿鞋的，人生不设限。",
    quote: "他们卷学历，我卷生存能力，最后谁先退休还不一定呢。"
  },
  "EBTI": {
    name: "温水煮蛙",
    img: "温水煮蛙.jpg",
    desc: "适配人群：大专/高职毕业生、普通本科选了不卷但学历心结解不开的矛盾人<br><br>最内耗的组合：选择了不卷，但学历的执念怎么也解不开；别人问起学历就闪躲，回去又开始怀疑人生。白天朋友圈发「躺平才是正经事」，晚上偷偷搜「成人本科报名截止了吗」。卷不动，放不下，躺不平，活得累。明明选了务实路线，偏偏过不了学历这关，天天跟自己较劲。",
    quote: "躺又躺不平，卷又卷不起，我的人生就是个温水煮蛙。"
  },
  "EBTO": {
    name: "执念佛系人",
    img: "执念佛系人.jpg",
    desc: "适配人群：早入社会的实干派、知道学历心结但能看开过来的过来人<br><br>心里清楚学历是自己的心结，但别人怎么看无所谓。自己闷头把日子过好，偶尔夜深人静会想「要是当初多考几分就好了」，第二天醒来该搬砖搬砖。不纠结别人的评价，但承认有自己的小遗憾，主打一个和自己和解。遗憾可以有，日子必须过，执念是调味品不是主菜。",
    quote: "学历是过去的遗憾，日子是现在的事业，遗憾可以有，日子不能停。"
  },
  "EPNI": {
    name: "表面佛背地比",
    img: "表面佛背地比.jpg",
    desc: "适配人群：大专/高职有一技之长的实干派、明面脱敏暗里攀比的矛盾体<br><br>聚会时说「学历算啥」，回家翻同学朋友圈翻到手酸。嘴上脱敏是社交面具，攀比内耗才是真实写照。在意的不是学历本身，而是「凭什么他学历比我高混得还比我好」。务实做事但不甘心，表面云淡风轻，背地里偷偷较劲，每一条比较都在心里扎了一根刺。",
    quote: "表面云淡风轻，背地翻同学朋友圈翻到手酸。"
  },
  "EPNO": {
    name: "实干体面人",
    img: "实干体面人.jpg",
    desc: "适配人群：大专/高职有过硬技能的实干派、在意门面但不纠结的社会达人<br><br>在意学历的门面，但不纠结。知道好学历是加分项，也接受自己的起点。比起学历标签，更在意实际能力能不能打，但该撑的场面绝不掉链子。脱敏但不躺平，攀比但不焦虑，务实又清醒，活得通透又体面。知道自己要什么，别人的评价只是参考。",
    quote: "学历不够实力凑，面子要挣日子更要过，主打一个清醒又体面。"
  },
  "EPTI": {
    name: "暗卷达人",
    img: "暗卷达人.jpg",
    desc: "适配人群：大专/高职拼命专升本、自考考研的隐形卷王<br><br>明明比谁都卷，嘴上说「随便试试」，考完才发现分数线最高的是自己。务实是底色，攀比是驱动力，学历执念是燃料，内耗是副作用。每张证书都是焦虑的战利品，攀比赢了也不心安，总觉得自己还差一截。世界上最怕的不是考不过，而是考过了依然不安。",
    quote: "嘴上说随便试试，复习资料堆得比谁都高。"
  },
  "EPTO": {
    name: "清醒卷王",
    img: "清醒卷王.jpg",
    desc: "适配人群：大专/高职考了专升本或自考、技能学历两手抓的实干卷王<br><br>在意学历title，也有学历执念，但看得很清楚：学历是工具，不是枷锁。该考的证考了，该升的学升了，不走弯路不纠结，务实又清醒地卷。知道自己要什么，别人说什么不重要，但title必须拿。卷得明明白白，看得清清楚楚，每一步都在轨道上。",
    quote: "卷得清醒，活得明白，我要的都会拿到手。"
  },
  "ABNI": {
    name: "双非躺平家",
    img: "双非躺平家.jpg",
    desc: "适配人群：双非二本/一本、四非本科毕业生，拒绝学历内耗的佛系党<br><br>高考差几分够不上211，考研卷不过985，考公是万年陪跑专业户，终于在某天彻底悟了：卷不动，就不卷了。找工作不冲大厂不看title，双休五险一金就是顶配；同学聚会从不主动提学校，别人问起就一句「普通本科」一笔带过。拒绝学历PUA，拒绝同辈焦虑，我的人生我做主，学历只是个敲门砖，敲不开门，我就砸门。",
    quote: "双非怎么了？我吃你家大米了？"
  },
  "ABNO": {
    name: "学历脱敏大师",
    img: "学历脱敏大师.jpg",
    desc: "适配人群：全学历段通用，反学历焦虑的人间清醒党<br><br>不管是大专还是985，早就对学历彻底脱敏了。找工作不看学校title，看实际能力；交朋友不看学历高低，看人品三观；亲戚问起学历，直接一句「没读过什么书」堵回去。彻底拒绝学历鄙视链，也拒绝学历自卑，清楚知道学历只是人生的一张入场券，不是判决书。人生是旷野，不是轨道，学历高低，都不耽误我活成自己想要的样子。",
    quote: "学历决定你的下限，但上限，从来都和学历没关系。"
  },
  "ABTI": {
    name: "暴躁摆烂人",
    img: "暴躁摆烂人.jpg",
    desc: "适配人群：二本/一本毕业生、想卷又卷不动、躺又躺不甘心的暴躁族<br><br>知道应该进取但选择了躺平，学历是心结但始终不肯动手，内心翻江倒海但身体稳如泰山。深夜下定决心「明天开始学习」，闹钟响了翻身继续睡，起来之后又骂自己不争气。每个深夜都在卷和躺之间反复横跳，最后跳到了焦虑的怀抱里。摆烂不是因为不想卷，是因为卷了怕白卷。",
    quote: "每天都在卷和躺之间反复横跳，最后跳到了焦虑的怀抱。"
  },
  "ABTO": {
    name: "摆烂哲学家",
    img: "摆烂哲学家.jpg",
    desc: "适配人群：二本/一本毕业生、有学历追求但选择摆烂的看开党<br><br>有进取心但选择了躺平，有学历执念但不内耗。知道学历重要，但更知道卷不动了。偶尔冒出考研的念头，看了看报名费又默默放下了。执念还在，通透也在，摆烂但不痛苦，也算一种另类人生智慧。想卷的时候翻两页书，不想卷的时候安心刷剧，主打一个弹性的人生态度。",
    quote: "考研报名费看了三天，最后还是点了关闭。"
  },
  "APNI": {
    name: "隐忍攀登者",
    img: "隐忍攀登者.jpg",
    desc: "适配人群：211/985毕业生、表面云淡风轻但内心暗暗比较的高学历选手<br><br>表面脱敏，说自己「就一普通211」，其实比谁都在意这个title。攀比是内驱力，内耗是副产品。不执着学历的本质但执着于它带来的光环效应，明明是脱敏体质却走不出攀比的引力场。聚会时轻描淡写提一下学校名字，回去就开始复盘「那谁是不是混得比我好」。",
    quote: "表面：就一普通学校。内心：但比你知道的强。"
  },
  "APNO": {
    name: "野心布道师",
    img: "野心布道师.jpg",
    desc: "适配人群：985/211/双一流毕业生、目标明确且不自耗的精英派<br><br>在意学历title但不被其绑架，有野心但不焦虑。清楚知道学历是自己的通行证，也是社交名片，坦然接受并利用它。不过度脱敏也不过度执着，把学历当工具，把野心当燃料，卷得明明白白。办公室里没有人不知道他毕业于哪所大学，但他从不需要主动提起——简历上的学校名已经替他发言了。",
    quote: "学历是我的通行证，野心是我的发动机，我卷故我在。"
  },
  "APTI": {
    name: "Title枷锁人",
    img: "Title枷锁人.jpg",
    desc: "适配人群：211/双一流、末流985毕业生，被名校光环绑架的内耗党<br><br>高考拿到录取通知书的那天，是全家的高光时刻，也是内耗的开始。这个211/985的title，既是别人眼里的光环，也是套在身上的枷锁。找工作不敢找低于预期的，怕对不起自己的学历；亲戚问话不敢说混得不好，怕丢了名校的脸；考研考公必须卷top，不然就是「学历贬值」。一辈子活在别人的期待里，嘴上说着「985也没用」，心里比谁都在意这个title。",
    quote: "考上名校的那一刻，我以为是人生的开始，没想到是人生的天花板。"
  },
  "APTO": {
    name: "天坑卷王",
    img: "天坑卷王.jpg",
    desc: "适配人群：985/top2本硕博、天坑专业科研人、一路卷到黑的学术党<br><br>从重点高中卷到top985，从本科卷到博士，回头一看，同龄人已经结婚生子买房买车，我还在实验室里熬大夜，拿着微薄的补助，对着发不出去的SCI掉头发。嘴上喊着「科研改变世界」，心里清楚「毕业即失业」，考公只能报三不限，企业招聘只要本科生，读了二十年书，最后发现学历越高，路越窄。",
    quote: "别人的二十岁风生水起，我的二十岁，不是在实验室，就是在去实验室的路上。"
  }
};

var dimPairs = {
  1: ["E", "A"],
  2: ["B", "P"],
  3: ["N", "T"],
  4: ["I", "O"]
};

var dimLabels = {
  1: { left: "求稳", right: "进取" },
  2: { left: "看淡", right: "攀比" },
  3: { left: "脱敏", right: "执念" },
  4: { left: "内耗", right: "通透" }
};

var currentQ = 0;
var dimScores = { 1: {}, 2: {}, 3: {}, 4: {} };
var answerHistory = [];

function resetScores() {
  for (var d = 1; d <= 4; d++) {
    dimScores[d] = {};
    dimPairs[d].forEach(function(v) { dimScores[d][v] = 0; });
  }
  answerHistory = [];
}

function saveState() {
  try {
    localStorage.setItem('ebti_state', JSON.stringify({
      currentQ: currentQ,
      dimScores: dimScores,
      answerHistory: answerHistory
    }));
  } catch (e) {}
}

function loadState() {
  try {
    var saved = localStorage.getItem('ebti_state');
    if (saved) {
      var state = JSON.parse(saved);
      currentQ = state.currentQ;
      dimScores = state.dimScores;
      answerHistory = state.answerHistory;
      return true;
    }
  } catch (e) {}
  return false;
}

function clearState() {
  try {
    localStorage.removeItem('ebti_state');
  } catch (e) {}
}

function showPage(id) {
  document.querySelectorAll('.page').forEach(function(p) { p.classList.remove('active'); });
  document.getElementById(id).classList.add('active');
}

function startTest() {
  currentQ = 0;
  resetScores();
  clearState();
  showQuestion();
  showPage('question');
}

function showQuestion() {
  var q = questions[currentQ];
  document.getElementById('q-num').textContent = currentQ + 1;
  document.getElementById('progress-fill').style.width = ((currentQ + 1) / questions.length * 100) + '%';
  document.getElementById('q-title').textContent = q.title;
  var optDom = document.getElementById('options');
  optDom.innerHTML = '';
  q.options.forEach(function(opt) {
    var btn = document.createElement('button');
    btn.textContent = opt.text;
    btn.onclick = function() { selectOption(q.dim, opt.val); };

    if (answerHistory[currentQ] && answerHistory[currentQ].val === opt.val) {
      btn.classList.add('selected');
    }

    optDom.appendChild(btn);
  });

  var prevBtn = document.getElementById('btn-prev');
  if (prevBtn) {
    prevBtn.style.display = currentQ > 0 ? 'inline-block' : 'none';
  }
}

function prevQuestion() {
  if (currentQ <= 0) return;
  currentQ--;
  var last = answerHistory[currentQ];
  dimScores[last.dim][last.val]--;
  answerHistory.splice(currentQ, 1);
  saveState();
  showQuestion();
}

function selectOption(dim, val) {
  dimScores[dim][val]++;
  answerHistory.push({ dim: dim, val: val });
  currentQ++;
  saveState();
  if (currentQ >= questions.length) {
    showResult();
  } else {
    showQuestion();
  }
}

function getResultType() {
  var result = '';
  for (var d = 1; d <= 4; d++) {
    var pair = dimPairs[d];
    var a = dimScores[d][pair[0]];
    var b = dimScores[d][pair[1]];
    if (a > b) {
      result += pair[0];
    } else if (b > a) {
      result += pair[1];
    } else {
      result += pair[Math.random() > 0.5 ? 0 : 1];
    }
  }
  return result;
}

function renderHTML(container, str) {
  container.innerHTML = '';
  var parts = str.split(/<br\s*\/?>/i);
  parts.forEach(function(part, i) {
    if (i > 0) {
      container.appendChild(document.createElement('br'));
    }
    container.appendChild(document.createTextNode(part));
  });
}

function showResult() {
  document.getElementById('progress-fill').style.width = '100%';
  var type = getResultType();
  var r = results[type];
  if (!r) {
    type = Object.keys(results)[Math.floor(Math.random() * Object.keys(results).length)];
    r = results[type];
  }
  document.getElementById('r-type').textContent = type;
  document.getElementById('r-name').textContent = r.name;
  var imgEl = document.getElementById('r-img');
  if (imgEl) { imgEl.src = 'png/' + encodeURIComponent(r.img); imgEl.alt = r.name; }
  renderHTML(document.getElementById('r-desc'), r.desc);
  document.getElementById('r-quote').textContent = r.quote;

  var reviewEl = document.getElementById('r-review');
  if (reviewEl) {
    reviewEl.innerHTML = '';
    var heading = document.createElement('p');
    heading.className = 'review-heading';
    heading.textContent = '你的答题回顾';
    reviewEl.appendChild(heading);
    answerHistory.forEach(function(ans, i) {
      var q = questions[i];
      var row = document.createElement('div');
      row.className = 'review-row';
      var num = document.createElement('span');
      num.className = 'review-num';
      num.textContent = (i + 1) + '.';
      var text = document.createElement('span');
      text.className = 'review-text';
      text.textContent = q.options.find(function(o) { return o.val === ans.val; }).text;
      row.appendChild(num);
      row.appendChild(text);
      reviewEl.appendChild(row);
    });
  }

  var dimsEl = document.getElementById('r-dims');
  if (dimsEl) {
    dimsEl.innerHTML = '';
    var dimsHeading = document.createElement('p');
    dimsHeading.className = 'review-heading';
    dimsHeading.textContent = '维度评分';
    dimsEl.appendChild(dimsHeading);

    var dimAxes = [
      { key: "A", label: "进取" },
      { key: "P", label: "攀比" },
      { key: "T", label: "执念" },
      { key: "I", label: "内耗" },
      { key: "E", label: "求稳" },
      { key: "B", label: "看淡" },
      { key: "N", label: "脱敏" },
      { key: "O", label: "通透" }
    ];

    var pctMap = {};
    for (var d = 1; d <= 4; d++) {
      var pair = dimPairs[d];
      var total = dimScores[d][pair[0]] + dimScores[d][pair[1]];
      pctMap[pair[0]] = Math.round(dimScores[d][pair[0]] / total * 100);
      pctMap[pair[1]] = 100 - pctMap[pair[0]];
    }

    var cx = 155, cy = 148, radius = 90;
    var svg = '';

    [0.33, 0.67, 1].forEach(function(level) {
      var pts = [];
      for (var i = 0; i < 8; i++) {
        var a = (i * Math.PI / 4) - Math.PI / 2;
        pts.push((cx + radius * level * Math.cos(a)).toFixed(1) + ',' + (cy + radius * level * Math.sin(a)).toFixed(1));
      }
      svg += '<polygon points="' + pts.join(' ') + '" fill="none" stroke="' + (level === 1 ? '#d1cfc5' : '#e8e6dc') + '" stroke-width="1"/>';
    });

    for (var i = 0; i < 8; i++) {
      var a = (i * Math.PI / 4) - Math.PI / 2;
      var ex = cx + radius * Math.cos(a);
      var ey = cy + radius * Math.sin(a);
      svg += '<line x1="' + cx + '" y1="' + cy + '" x2="' + ex.toFixed(1) + '" y2="' + ey.toFixed(1) + '" stroke="#e8e6dc" stroke-width="1"/>';
    }

    var dataPts = [];
    for (var i = 0; i < 8; i++) {
      var a = (i * Math.PI / 4) - Math.PI / 2;
      var pct = Math.max(pctMap[dimAxes[i].key], 8) / 100;
      dataPts.push((cx + radius * pct * Math.cos(a)).toFixed(1) + ',' + (cy + radius * pct * Math.sin(a)).toFixed(1));
    }
    svg += '<polygon points="' + dataPts.join(' ') + '" fill="rgba(201,100,66,0.15)" stroke="#c96442" stroke-width="2" stroke-linejoin="round"/>';

    for (var i = 0; i < 8; i++) {
      var a = (i * Math.PI / 4) - Math.PI / 2;
      var pct = Math.max(pctMap[dimAxes[i].key], 8) / 100;
      var px = cx + radius * pct * Math.cos(a);
      var py = cy + radius * pct * Math.sin(a);
      svg += '<circle cx="' + px.toFixed(1) + '" cy="' + py.toFixed(1) + '" r="3.5" fill="#c96442"/>';
    }

    for (var i = 0; i < 8; i++) {
      var a = (i * Math.PI / 4) - Math.PI / 2;
      var cosA = Math.cos(a);
      var sinA = Math.sin(a);
      var labelR = radius + 24;
      var lx = cx + labelR * cosA;
      var ly = cy + labelR * sinA;
      var anchor = 'middle';
      var dy1 = 5;
      var dx = 0;

      if (cosA > 0.3) { anchor = 'start'; dx = 4; }
      else if (cosA < -0.3) { anchor = 'end'; dx = -4; }
      if (sinA < -0.7) { dy1 = -5; }
      else if (sinA > 0.7) { dy1 = 14; }

      svg += '<text x="' + (lx + dx).toFixed(1) + '" y="' + (ly + dy1).toFixed(1) + '" text-anchor="' + anchor + '" font-size="13" font-weight="500" fill="#4d4c48" font-family="Inter,system-ui,-apple-system,Arial,sans-serif">' + dimAxes[i].label + '</text>';
      svg += '<text x="' + (lx + dx).toFixed(1) + '" y="' + (ly + dy1 + 15).toFixed(1) + '" text-anchor="' + anchor + '" font-size="11" font-weight="500" fill="#c96442" font-family="Inter,system-ui,-apple-system,Arial,sans-serif">' + pctMap[dimAxes[i].key] + '%</text>';
    }

    var svgWrap = document.createElement('div');
    svgWrap.className = 'radar-wrap';
    svgWrap.innerHTML = '<svg viewBox="0 0 310 300" width="100%" xmlns="http://www.w3.org/2000/svg">' + svg + '</svg>';
    dimsEl.appendChild(svgWrap);
  }

  clearState();
  showPage('result');
}

function copyResult() {
  var type = document.getElementById('r-type').textContent;
  var name = document.getElementById('r-name').textContent;
  var quote = document.getElementById('r-quote').textContent;
  var text = "我的EBTI学历人设是 " + type + "「" + name + "」\n" + quote + "\n\n快来测测你的EBTI学历人格！";
  if (navigator.clipboard) {
    navigator.clipboard.writeText(text).then(function() { showToast('已复制，快去分享吧'); });
  } else {
    var ta = document.createElement('textarea');
    ta.value = text;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
    showToast('已复制，快去分享吧');
  }
}

function saveDimImage() {
  var dimAxes = [
    { key: "A", label: "进取" },
    { key: "P", label: "攀比" },
    { key: "T", label: "执念" },
    { key: "I", label: "内耗" },
    { key: "E", label: "求稳" },
    { key: "B", label: "看淡" },
    { key: "N", label: "脱敏" },
    { key: "O", label: "通透" }
  ];

  var pctMap = {};
  for (var d = 1; d <= 4; d++) {
    var pair = dimPairs[d];
    var total = dimScores[d][pair[0]] + dimScores[d][pair[1]];
    pctMap[pair[0]] = Math.round(dimScores[d][pair[0]] / total * 100);
    pctMap[pair[1]] = 100 - pctMap[pair[0]];
  }

  var type = document.getElementById('r-type').textContent;
  var name = document.getElementById('r-name').textContent;
  var quote = document.getElementById('r-quote').textContent;
  var r = results[type];

  var avatarDataUrl = (avatarImages && r && r.img) ? avatarImages[r.img] : null;
  var avImg = null;
  if (avatarDataUrl) {
    avImg = new Image();
    avImg.src = avatarDataUrl;
  }

  function buildCanvas() {
    var scale = 2;
    var W = 380;
    var badgeTop = 16, badgeH = 28;
    var titleY = 88, nameY = 116;
    var avatarSize = 110;
    var avatarGap = 16;
    var avatarY = nameY + avatarGap;
    var hasAvatar = avImg && avImg.complete && avImg.naturalWidth > 0;
    var avatarBottom = hasAvatar ? avatarY + avatarSize : avatarY;
    var radarGap = hasAvatar ? 20 : 0;
    var cy = avatarBottom + radarGap + 120;
    var radius = 100;
    var labelBottom = cy + radius + 40;
    var dividerY = labelBottom + 16;
    var quoteY = dividerY + 24;
    var footerY = quoteY + 60;
    var H = footerY + 20;

    var canvas = document.createElement('canvas');
    canvas.width = W * scale;
    canvas.height = H * scale;
    var ctx = canvas.getContext('2d');
    ctx.scale(scale, scale);

    ctx.fillStyle = '#f5f4ed';
    ctx.fillRect(0, 0, W, H);

    ctx.fillStyle = '#e8e6dc';
    roundRect(ctx, W / 2 - 65, badgeTop, 130, badgeH, 14);
    ctx.fill();
    ctx.font = '500 12px Inter, system-ui, -apple-system, Arial, sans-serif';
    ctx.fillStyle = '#c96442';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'bottom';
    ctx.fillText('\u4F60\u7684EBTI\u4EBA\u683C', W / 2, badgeTop + 20);

    ctx.font = '500 44px Georgia, Times New Roman, serif';
    ctx.fillStyle = '#c96442';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'alphabetic';
    ctx.fillText(type, W / 2, titleY);

    ctx.font = '500 20px Georgia, Times New Roman, serif';
    ctx.fillStyle = '#3d3d3a';
    ctx.fillText(name, W / 2, nameY);

    if (hasAvatar) {
      var ax = W / 2 - avatarSize / 2;
      ctx.save();
      roundRect(ctx, ax, avatarY, avatarSize, avatarSize, 12);
      ctx.clip();
      ctx.drawImage(avImg, ax, avatarY, avatarSize, avatarSize);
      ctx.restore();
      ctx.strokeStyle = '#e8e6dc';
      ctx.lineWidth = 2;
      roundRect(ctx, ax, avatarY, avatarSize, avatarSize, 12);
      ctx.stroke();
    }

    var cx = W / 2;

    [0.33, 0.67, 1].forEach(function(level) {
      ctx.beginPath();
      for (var i = 0; i < 8; i++) {
        var a = (i * Math.PI / 4) - Math.PI / 2;
        var x = cx + radius * level * Math.cos(a);
        var y = cy + radius * level * Math.sin(a);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.closePath();
      ctx.strokeStyle = level === 1 ? '#d1cfc5' : '#e8e6dc';
      ctx.lineWidth = 1;
      ctx.stroke();
    });

    for (var i = 0; i < 8; i++) {
      var a = (i * Math.PI / 4) - Math.PI / 2;
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.lineTo(cx + radius * Math.cos(a), cy + radius * Math.sin(a));
      ctx.strokeStyle = '#e8e6dc';
      ctx.lineWidth = 1;
      ctx.stroke();
    }

    ctx.beginPath();
    for (var i = 0; i < 8; i++) {
      var a = (i * Math.PI / 4) - Math.PI / 2;
      var pct = Math.max(pctMap[dimAxes[i].key], 8) / 100;
      var x = cx + radius * pct * Math.cos(a);
      var y = cy + radius * pct * Math.sin(a);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.closePath();
    ctx.fillStyle = 'rgba(201,100,66,0.15)';
    ctx.fill();
    ctx.strokeStyle = '#c96442';
    ctx.lineWidth = 2;
    ctx.stroke();

    for (var i = 0; i < 8; i++) {
      var a = (i * Math.PI / 4) - Math.PI / 2;
      var pct = Math.max(pctMap[dimAxes[i].key], 8) / 100;
      var x = cx + radius * pct * Math.cos(a);
      var y = cy + radius * pct * Math.sin(a);
      ctx.beginPath();
      ctx.arc(x, y, 4, 0, Math.PI * 2);
      ctx.fillStyle = '#c96442';
      ctx.fill();
    }

    ctx.textBaseline = 'middle';
    for (var i = 0; i < 8; i++) {
      var a = (i * Math.PI / 4) - Math.PI / 2;
      var cosA = Math.cos(a);
      var sinA = Math.sin(a);
      var axisEndX = cx + radius * cosA;
      var axisEndY = cy + radius * sinA;

      var anchorX, anchorY, align;
      if (Math.abs(sinA) > 0.9) {
        anchorX = axisEndX;
        anchorY = axisEndY + (sinA > 0 ? 22 : -22);
        align = 'center';
      } else if (Math.abs(cosA) > 0.9) {
        anchorX = axisEndX + (cosA > 0 ? 16 : -16);
        anchorY = axisEndY;
        align = cosA > 0 ? 'left' : 'right';
      } else {
        anchorX = axisEndX + (cosA > 0 ? 18 : -18);
        anchorY = axisEndY + (sinA > 0 ? 12 : -12);
        align = cosA > 0 ? 'left' : 'right';
      }

      ctx.textAlign = align;
      ctx.font = '600 14px Inter, system-ui, -apple-system, Arial, sans-serif';
      ctx.fillStyle = '#4d4c48';
      ctx.fillText(dimAxes[i].label, anchorX, anchorY - 8);
      ctx.font = '500 11px Inter, system-ui, -apple-system, Arial, sans-serif';
      ctx.fillStyle = '#c96442';
      ctx.fillText(pctMap[dimAxes[i].key] + '%', anchorX, anchorY + 9);
    }

    ctx.textBaseline = 'alphabetic';
    ctx.fillStyle = '#e8e6dc';
    ctx.fillRect(40, dividerY, W - 80, 1);

    ctx.font = 'italic 500 14px Georgia, Times New Roman, serif';
    ctx.fillStyle = '#141413';
    ctx.textAlign = 'center';
    wrapText(ctx, '\u300C' + quote + '\u300D', W / 2, quoteY, W - 80, 24);

    ctx.font = '400 11px Inter, system-ui, -apple-system, Arial, sans-serif';
    ctx.fillStyle = '#87867f';
    ctx.textAlign = 'center';
    ctx.fillText('EBTI - \u5B66\u5386\u81EA\u5632\u4EBA\u683C\u6D4B\u8BD5', W / 2, footerY);

    try {
      canvas.toBlob(function(blob) {
        if (!blob) { fallbackSave(canvas, type); return; }
        var url = URL.createObjectURL(blob);
        var a = document.createElement('a');
        a.href = url;
        a.download = 'EBTI-' + type + '.png';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        showToast('\u7EF4\u5EA6\u56FE\u5DF2\u4FDD\u5B58');
      }, 'image/png');
    } catch (e) {
      fallbackSave(canvas, type);
    }
  }

  if (avImg) {
    if (avImg.complete && avImg.naturalWidth > 0) {
      buildCanvas();
    } else {
      avImg.onload = function() { buildCanvas(); };
      avImg.onerror = function() { avImg = null; buildCanvas(); };
    }
  } else {
    buildCanvas();
  }
}

function fallbackSave(canvas, type) {
  try {
    var dataURL = canvas.toDataURL('image/png');
    var a = document.createElement('a');
    a.href = dataURL;
    a.download = 'EBTI-' + type + '.png';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    showToast('维度图已保存');
  } catch (e2) {
    showToast('保存失败，请截图保存');
  }
}

function roundRect(ctx, x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.lineTo(x + w - r, y);
  ctx.quadraticCurveTo(x + w, y, x + w, y + r);
  ctx.lineTo(x + w, y + h - r);
  ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
  ctx.lineTo(x + r, y + h);
  ctx.quadraticCurveTo(x, y + h, x, y + h - r);
  ctx.lineTo(x, y + r);
  ctx.quadraticCurveTo(x, y, x + r, y);
  ctx.closePath();
}

function wrapText(ctx, text, x, y, maxWidth, lineHeight) {
  var chars = text.split('');
  var line = '';
  var lineY = y;
  for (var i = 0; i < chars.length; i++) {
    var testLine = line + chars[i];
    var metrics = ctx.measureText(testLine);
    if (metrics.width > maxWidth && line.length > 0) {
      ctx.fillText(line, x, lineY);
      line = chars[i];
      lineY += lineHeight;
    } else {
      line = testLine;
    }
  }
  ctx.fillText(line, x, lineY);
}

function showToast(msg) {
  var old = document.querySelector('.toast');
  if (old) old.remove();
  var t = document.createElement('div');
  t.className = 'toast';
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(function() { t.remove(); }, 2000);
}

function restart() {
  startTest();
}

var savedState = loadState();
if (savedState && currentQ > 0 && currentQ < questions.length) {
  showQuestion();
  showPage('question');
} else {
  clearState();
  showPage('start');
}