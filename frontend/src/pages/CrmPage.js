import React, { useState, useEffect } from 'react';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import { getBoards, getColumnsByBoard, getCardsByColumn, updateCard } from '../services/api'; // Assuming API functions exist
import { useAuth } from '../contexts/AuthContext';
import './CrmPage.css'; // Create this CSS file for styling

// --- Card Component ---
const CardComponent = ({ card, index }) => {
    return (
        <Draggable draggableId={String(card.id)} index={index}>
            {(provided, snapshot) => (
                <div
                    ref={provided.innerRef}
                    {...provided.draggableProps}
                    {...provided.dragHandleProps}
                    className={`crm-card ${snapshot.isDragging ? 'dragging' : ''}`}
                >
                    <h4>{card.titulo}</h4>
                    <p>{card.descricao || 'Sem descrição'}</p>
                    {/* Add tags or other info later */}
                </div>
            )}
        </Draggable>
    );
};

// --- Column Component ---
const ColumnComponent = ({ column, cards }) => {
    return (
        <div className="crm-column">
            <h3>{column.nome}</h3>
            <Droppable droppableId={String(column.id)} type="card">
                {(provided, snapshot) => (
                    <div
                        ref={provided.innerRef}
                        {...provided.droppableProps}
                        className={`crm-card-list ${snapshot.isDraggingOver ? 'dragging-over' : ''}`}
                    >
                        {cards.map((card, index) => (
                            <CardComponent key={card.id} card={card} index={index} />
                        ))}
                        {provided.placeholder}
                    </div>
                )}
            </Droppable>
            {/* Add button to create new card later */}
        </div>
    );
};

// --- Board Component (Main Page Logic) ---
function CrmPage() {
    const [board, setBoard] = useState(null); // Assuming one board for simplicity for now
    const [columns, setColumns] = useState({}); // { columnId: { id, nome, cards: [cardId1, cardId2] } }
    const [cards, setCards] = useState({}); // { cardId: { id, titulo, ... } }
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const { user } = useAuth();

    // Fetch initial board data
    useEffect(() => {
        const loadBoardData = async () => {
            if (!user?.empresa_id) {
                setError('Usuário não associado a uma empresa.');
                setLoading(false);
                return;
            }
            try {
                setLoading(true);
                // 1. Fetch boards for the company (for now, assume the first one)
                const userBoards = await getBoards(); // API fetches boards for the current user's company
                if (!userBoards || userBoards.length === 0) {
                    // Optional: Create a default board if none exists?
                    setError('Nenhum quadro Kanban encontrado para esta empresa.');
                    setLoading(false);
                    return;
                }
                const currentBoard = userBoards[0]; // Use the first board
                setBoard(currentBoard);

                // 2. Fetch columns for the board
                const boardColumns = await getColumnsByBoard(currentBoard.id);
                
                const columnsData = {};
                const cardsData = {};
                const columnPromises = boardColumns.map(async (col) => {
                    // 3. Fetch cards for each column
                    const columnCards = await getCardsByColumn(col.id);
                    columnsData[col.id] = { ...col, cardIds: columnCards.map(c => c.id) };
                    columnCards.forEach(card => {
                        cardsData[card.id] = card;
                    });
                });

                await Promise.all(columnPromises);

                setColumns(columnsData);
                setCards(cardsData);
                setError('');
            } catch (err) {
                setError('Falha ao carregar dados do quadro Kanban.');
                console.error(err);
            } finally {
                setLoading(false);
            }
        };

        loadBoardData();
    }, [user]);

    // Handle Drag and Drop
    const onDragEnd = async (result) => {
        const { destination, source, draggableId } = result;

        // No destination or dropped in the same place
        if (!destination || (destination.droppableId === source.droppableId && destination.index === source.index)) {
            return;
        }

        const startColumn = columns[source.droppableId];
        const finishColumn = columns[destination.droppableId];
        const draggedCard = cards[draggableId];

        // --- Optimistic UI Update --- 

        // Moving within the same column
        if (startColumn.id === finishColumn.id) {
            const newCardIds = Array.from(startColumn.cardIds);
            newCardIds.splice(source.index, 1);
            newCardIds.splice(destination.index, 0, parseInt(draggableId));

            const newColumn = {
                ...startColumn,
                cardIds: newCardIds,
            };

            setColumns(prevColumns => ({
                ...prevColumns,
                [newColumn.id]: newColumn,
            }));

            // --- Backend Update --- 
            try {
                // Update card order (backend needs logic for this, or update all cards in column)
                // For MVP, let's just update the moved card's column (even if same) and order (approximate)
                await updateCard(draggableId, { coluna_id: finishColumn.id, ordem: destination.index }); 
            } catch (err) {
                setError('Falha ao atualizar ordem do card. Revertendo.');
                console.error(err);
                // Revert UI on error
                setColumns(prevColumns => ({
                    ...prevColumns,
                    [startColumn.id]: startColumn, 
                }));
            }
            return;
        }

        // Moving to a different column
        const startCardIds = Array.from(startColumn.cardIds);
        startCardIds.splice(source.index, 1);
        const newStartColumn = {
            ...startColumn,
            cardIds: startCardIds,
        };

        const finishCardIds = Array.from(finishColumn.cardIds);
        finishCardIds.splice(destination.index, 0, parseInt(draggableId));
        const newFinishColumn = {
            ...finishColumn,
            cardIds: finishCardIds,
        };

        setColumns(prevColumns => ({
            ...prevColumns,
            [newStartColumn.id]: newStartColumn,
            [newFinishColumn.id]: newFinishColumn,
        }));

         // --- Backend Update --- 
         try {
            // Update the card's column_id and approximate order
            await updateCard(draggableId, { coluna_id: finishColumn.id, ordem: destination.index }); 
        } catch (err) {
            setError('Falha ao mover card. Revertendo.');
            console.error(err);
            // Revert UI on error
            setColumns(prevColumns => ({
                ...prevColumns,
                [startColumn.id]: startColumn,
                [finishColumn.id]: finishColumn,
            }));
        }
    };

    if (loading) return <p>Carregando quadro Kanban...</p>;
    if (error) return <p style={{ color: 'red' }}>{error}</p>;
    if (!board) return <p>Nenhum quadro Kanban configurado.</p>;

    // Get columns in order (if order field exists, otherwise default order)
    const orderedColumnIds = Object.values(columns).sort((a, b) => (a.ordem || 0) - (b.ordem || 0)).map(c => c.id);

    return (
        <div className="crm-page">
            <h2>Quadro Kanban: {board.nome}</h2>
            <DragDropContext onDragEnd={onDragEnd}>
                <div className="crm-board">
                    {orderedColumnIds.map(columnId => {
                        const column = columns[columnId];
                        const columnCards = column.cardIds.map(cardId => cards[cardId]).filter(Boolean); // Filter out potential undefined cards
                        return <ColumnComponent key={column.id} column={column} cards={columnCards} />;
                    })}
                </div>
            </DragDropContext>
            {/* Add button to create new column later */}
        </div>
    );
}

export default CrmPage;

