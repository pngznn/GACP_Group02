seo_optimizer.js
function goTo(n) {
    document.querySelectorAll('.seo-screen').forEach(s => s.classList.remove('active'));
    document.getElementById('screen' + n).classList.add('active');

    // Populate screen 2 from screen 1 inputs
    if (n === 2) {
        const title = document.getElementById('s1_title').value || 'Untitled Article';
        const content = document.getElementById('s1_content').value || '';
        document.getElementById('s2_title_display').textContent = title;
        const words = content.trim() ? content.trim().split(/\s+/).length : 0;
        document.getElementById('s2_wordcount').textContent = words + ' words';

        const headings = (content.match(/^#{1,3} .+/gm) || []).length;
        document.getElementById('s2_headings').textContent = headings + ' headings';
    }

    if (n === 5) updateWordCount();
}

function removeTag(el) {
    el.closest('.k-tag').remove();
}

function addKeyword() {
    const input = document.getElementById('s2_kw_input');
    const val = input.value.trim();
    if (!val) return;
    const tag = document.createElement('span');
    tag.className = 'k-tag';
    tag.innerHTML = val + ' <span class="remove" onclick="removeTag(this)">×</span>';
    document.getElementById('s2_kw_tags').appendChild(tag);
    input.value = '';
}

document.getElementById('s2_kw_input')?.addEventListener('keydown', e => {
    if (e.key === 'Enter') { e.preventDefault(); addKeyword(); }
});

function selectType(btn) {
    document.querySelectorAll('.type-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
}

function updateWordCount() {
    const textarea = document.getElementById('s5_content');
    const el = document.getElementById('s5_wordcount');
    if (textarea && el) {
        const count = textarea.value.trim() ? textarea.value.trim().split(/\s+/).length : 0;
        el.textContent = count;
    }
}

document.getElementById('s5_content')?.addEventListener('input', updateWordCount);