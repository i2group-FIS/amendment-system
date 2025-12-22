import React from 'react';
import { useParams } from 'react-router-dom';

function AmendmentDetail() {
  const { id } = useParams();

  return (
    <div>
      <h1>Amendment Detail</h1>
      <p>Amendment ID: {id}</p>
      <p>This page is under construction.</p>
    </div>
  );
}

export default AmendmentDetail;
