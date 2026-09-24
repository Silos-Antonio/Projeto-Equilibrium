const inicio = document.querySelector('#data_hora');
const duracao = document.querySelector('#duracao_minutos');
const fimPrevisto = document.querySelector('#fim-previsto');

const modalEditar = document.querySelector('#modal-editar');
const formEditar = document.querySelector('#form-editar');
const editDataHora = document.querySelector('#edit_data_hora');


function atualizarFimPrevisto() {
    if (!inicio || !duracao || !fimPrevisto) {
        return;
    }

    if (!inicio.value || !duracao.value) {
        fimPrevisto.textContent =
            'Escolha o horário para ver o término.';

        return;
    }

    const fim = new Date(inicio.value);

    fim.setMinutes(
        fim.getMinutes() + Number(duracao.value)
    );

    fimPrevisto.textContent =
        'Termina em ' +
        fim.toLocaleString(
            'pt-BR',
            {
                dateStyle: 'short',
                timeStyle: 'short'
            }
        );
}


function abrirModalEdicao(id, dataHoraAtual) {
    if (!formEditar || !editDataHora || !modalEditar) {
        return;
    }

    formEditar.action =
        `/agendamentos/${id}/editar`;

    editDataHora.value = dataHoraAtual;

    modalEditar.showModal();
}


function fecharModalEdicao() {
    if (!modalEditar) {
        return;
    }

    modalEditar.close();
}


if (inicio && duracao) {
    inicio.addEventListener(
        'input',
        atualizarFimPrevisto
    );

    duracao.addEventListener(
        'input',
        atualizarFimPrevisto
    );
}

window.abrirModalEdicao = abrirModalEdicao;
window.fecharModalEdicao = fecharModalEdicao;