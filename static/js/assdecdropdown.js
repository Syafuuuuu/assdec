function updateOptions() {
    const assetType = document.getElementById('assetType').value;
    const subAssetType = document.getElementById('subAssetType');

    // Clear existing options
    subAssetType.innerHTML = '';

    // Populate options based on asset type
    if (assetType === 'Movable') {
      const movableAssetTypes = ['Cash/Bank Account', 'Motor Vehicles', 'Shares, Stock, Bonds and Securities', 'Jewelleries', 'Licenses and Permits', 'Other Valuables'];
      for (const movableAssetType of movableAssetTypes) {
        const option = document.createElement('option');
        option.value = movableAssetType;
        option.textContent = movableAssetType;

        subAssetType.appendChild(option);
      }
    } else if (assetType === 'Immovable') {
      const immovableAssetTypes = ['Land', 'Landed Property', 'Business owned by Families'];
      for (const immovableAssetType of immovableAssetTypes) {
        const option = document.createElement('option');
        option.value = immovableAssetType;
        option.textContent = immovableAssetType;

        subAssetType.appendChild(option);
      }
    } else {
      // No options for other asset types
    }
  }