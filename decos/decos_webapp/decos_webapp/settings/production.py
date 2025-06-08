<form method="post">
  <div class="card p-4 mb-4 shadow-sm">
    <div class="card-body">
      <h4>General experiment information</h4>
      <div class="row">
        <div class="col-md-6">
          <label for="id_name">Name:</label>
          <input type="text" name="name" maxlength="100" required id="id_name" class="form-control">
        </div>
        <div class="col-md-6">
          <label for="id_description">Description:</label>
          <textarea name="description" cols="40" rows="10" id="id_description" class="form-control"></textarea>
        </div>
      </div>
    </div>
  </div>
</form>
<form method="post" action="/create_dmp/">
  <button type="submit" class="btn btn-primary">Create new DMP</button>
</form>
